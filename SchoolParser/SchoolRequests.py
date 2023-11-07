import requests
from SchoolParser.Events import Events


class Request:
    def __init__(self, cookies: dict, headers: dict):
        self.cookies = cookies
        self.headers = headers
        self.url = 'https://edu.21-school.ru/services/graphql'
        self.events = Events()

    def get_json_data(self, operation_name: str, query: str, limit: int, variables: dict):
        json_data = {
            'operationName': operation_name,
            'variables': variables,
            'query': query
        }

        return json_data

    def send_post_request(self, operation_name: str, query: str, limit: int = 0, variables: dict = {}):
        response = requests.post(self.url, cookies=self.cookies, headers=self.headers,
                                 json=self.get_json_data(operation_name, query, limit, variables)).json()

        return response

    def get_events(self, limit: int = 6, print_result: bool = True, only_notify: bool = False):
        query_request = ('query getAgendaEvents($from: DateTime!, $to: DateTime!, $limit: Int!) {\n  calendarEventS21 '
                         '{\n    getMyAgendaEvents(from: $from, to: $to, limit: $limit) {\n      agendaItemContext {\n'
                         '        entityId\n        entityType\n        __typename\n      }\n      start\n      end\n  '
                         '    label\n      description\n      agendaEventType\n      additionalInfo {\n        key\n   '
                         '     value\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n')
        variables = {
            'from': self.events.get_from_to_date(),
            'to': self.events.get_from_to_date('to'),
            'limit': limit,
        }

        response = self.send_post_request(operation_name='getAgendaEvents', query=query_request, limit=limit,
                                          variables=variables)

        if only_notify:
            return self.get_peer_review_event(response)

        result = {}

        for idx, event in enumerate(response['data']['calendarEventS21']['getMyAgendaEvents'], 1):
            start_time = self.events.get_datetime_start_event(event['start'])
            event_info = {
                'Имя': event['label'],
                'Описание': event['description'],
                'Начало через': start_time if start_time else 'Уже началось'
            }
            event_key = f'Ивент #{idx}'

            result[event_key] = event_info
            if print_result:
                print(f'\033[1m\033[31m{event_key}\033[0m')
                for info_name, info_value in event_info.items():
                    print(f'\033[1m\033[35m{info_name}\033[0m: \033[37m{info_value}\033[0m')

        return result if not print_result else None

    def get_peer_review_event(self, response):
        result = {}
        for event in response['data']['calendarEventS21']['getMyAgendaEvents']:
            start_time = self.events.get_datetime_start_event(event['start'], notify=True)
            if (start_time and (event['label'] == 'Participant Peer Review' or
                                event['label'] == "Participant project presentation")):
                result = {
                    'Описание': event['description'],
                    'Начало через': start_time
                }

        return result

    def get_user_info(self, print_result: bool = True):
        query_request = ('query getCurrentUser {\n  user {\n    getCurrentUser {\n      ...CurrentUser\n      '
                         '__typename\n    }\n    __typename\n  }\n  student {\n    getExperience {\n      '
                         '...CurrentUserExperience\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment '
                         'CurrentUser on User {\n  id\n  avatarUrl\n  login\n  firstName\n  middleName\n  lastName\n'
                         '  currentSchoolStudentId\n  __typename\n}\n\nfragment CurrentUserExperience on UserExperience'
                         ' {\n  id\n  cookiesCount\n  codeReviewPoints\n  coinsCount\n  level {\n    id\n    range {\n '
                         '     id\n      levelCode\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n')
        response = self.send_post_request(operation_name='getCurrentUser', query=query_request)['data']

        result = {
            'Логин': response['user']['getCurrentUser']['login'],
            'Имя на портале': response['user']['getCurrentUser']['firstName'],
            'Фамилия на портале': response['user']['getCurrentUser']['lastName'],
            'Уровень': response['student']['getExperience']['level']['range']['levelCode'],
            'Количество peer поинтов': response['student']['getExperience']['cookiesCount'],
            'Количество code review поинтов': response['student']['getExperience']['codeReviewPoints'],
            'Количество coins': response['student']['getExperience']['coinsCount'],
            'Количество пенальти': self.get_penalty_info(),
            'Дедлайн': self.get_deadline_info()
        }

        if print_result:
            for info_key, info_value in result.items():
                print(f'\033[1m\033[35m{info_key}\033[0m: \033[37m{info_value}\033[0m')

        return result if not print_result else None

    def get_penalty_info(self):
        query_request = ('query getPenaltiesCount($statuses: [String]!) {\n  penalty {\n    countMy'
                         'Penalties(statuses: $statuses)\n    __typename\n  }\n}\n')
        variables = {
            'statuses': [
                'Scheduled',
            ],
        }
        response = self.send_post_request(operation_name='getPenaltiesCount', query=query_request, variables=variables)

        return response['data']['penalty']['countMyPenalties']

    def get_deadline_info(self):
        query_request = ('query deadlinesGetDeadlines($deadlineStatuses: [DeadlineStatus!]!, $page: PagingInput!, '
                         '$deadlinesFrom: DateTime, $deadlinesTo: DateTime, $sorting: [SortingField]) {\n  student '
                         '{\n    getDeadlines(\n      deadlineStatuses: $deadlineStatuses\n      page: $page\n      '
                         'deadlineFrom: $deadlinesFrom\n      deadlineTo: $deadlinesTo\n      sorting: $sorting\n    )'
                         ' {\n      deadline {\n        ...DeadlineData\n        __typename\n      }\n      '
                         'shiftRequests {\n        deadlineShiftRequestId\n        status\n        daysToShift\n'
                         '        createTs\n        __typename\n      }\n      deadlineGoal {\n       '
                         ' ...DeadlineGoalData\n        __typename\n      }\n      shiftCount\n      __typename\n   '
                         ' }\n    __typename\n  }\n}\n\nfragment DeadlineData on Deadline {\n  deadlineId\n  '
                         'description\n  comment\n  deadlineToDaysArray\n  deadlineTs\n  createTs\n  updateTs\n  '
                         'status\n  rules {\n    logicalOperatorId\n    rulesInGroup {\n      logicalOperatorId\n     '
                         ' value {\n        fieldId\n        subFieldKey\n        operator\n        value\n        '
                         '__typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\n'
                         'fragment DeadlineGoalData on DeadlineGoal {\n  goalProjects {\n    studentGoalId\n    '
                         'project {\n      goalName\n      goalId\n      __typename\n    }\n    status\n    '
                         'executionType\n    finalPercentage\n    finalPoint\n    pointTask\n    __typename\n  }\n  '
                         'goalCourses {\n    ...GoalCourse\n    __typename\n  }\n  levels {\n    ...Level\n    '
                         '__typename\n  }\n  __typename\n}\n\nfragment GoalCourse on CourseCoverInformation {\n  '
                         'localCourseId\n  courseName\n  courseType\n  experienceFact\n  finalPercentage\n  '
                         'displayedCourseStatus\n  __typename\n}\n\nfragment Level on ExperienceLevelRange {\n  id\n  '
                         'level\n  levelCode\n  leftBorder\n  rightBorder\n  __typename\n}\n')
        variables = {
            'page': {
                'limit': 1,
                'offset': 0,
            },
            'deadlineStatuses': [
                'OPEN',
                'SHIFTED',
            ],
            'sorting': {
                'name': 'deadlineTs',
                'asc': True,
            },
        }
        response = self.send_post_request(operation_name='deadlinesGetDeadlines', query=query_request,
                                          variables=variables)['data']['student']['getDeadlines'][0]['deadline']
        return (f"\n\t\t\t\tЦель - {response['description']}\n\t\t\t\t"
                f"Осталось - {self.events.get_datetime_start_event(response['deadlineTs'])}")

    def get_campus_plan_occupied(self, cluster_name: str = 'all', print_result: bool = True):
        common_value = {
            'clarity': {
                'id': '29992',
                'number_seats': 42
            },
            'serenity': {
                'id': '29991',
                'number_seats': 65
            },
            'tranquility': {
                'id': '29990',
                'number_seats': 53
            },
            'existense': {
                'id': '29988',
                'number_seats': 34
            },
            'genesis': {
                'id': '29987',
                'number_seats': 59
            },
            'presense': {
                'id': '29989',
                'number_seats': 42
            },
            'infinity': {
                'id': '29984',
                'number_seats': 59
            },
            'obscurity': {
                'id': '29985',
                'number_seats': 72
            },
            'silence': {
                'id': '29986',
                'number_seats': 42
            }
        }
        clusters = {
            'all': common_value
        }

        if cluster_name == 'all':
            clusters = common_value
        else:
            clusters = {cluster_name: common_value.get(cluster_name)}

        res = {}
        for cluster_name, cluster_info in clusters.items():
            cluster_plan = self.get_cluster_plan_occupied(cluster_id=cluster_info['id'],
                                                          number_seats=cluster_info['number_seats'],
                                                          cluster_name=cluster_name,
                                                          print_result=print_result)
            if not print_result: res.update(cluster_plan)

        return res

    def get_cluster_plan_occupied(self, cluster_id: str, number_seats: int, cluster_name: str,
                                  print_result: bool = True):
        query_request = ('query getCampusPlanOccupied($clusterId: ID!) {\n  student {\n    '
                         'getClusterPlanStudentsByClusterId(clusterId: $clusterId) {\n      occupiedPlaces '
                         '{\n        row\n        number\n        stageGroupName\n        stageName\n        '
                         'user {\n          id\n          login\n          avatarUrl\n          __typename\n        '
                         '}\n        experience {\n          id\n          value\n          level {\n            '
                         'id\n            range {\n              id\n              levelCode\n              '
                         'leftBorder\n              rightBorder\n              __typename\n            }\n            '
                         '__typename\n          }\n          __typename\n        }\n        studentType\n        '
                         '__typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n')
        variables = {
            'clusterId': cluster_id,
        }
        response = self.send_post_request(operation_name='getCampusPlanOccupied', query=query_request,
                                          variables=variables)

        occupied_places = response['data']['student']['getClusterPlanStudentsByClusterId']['occupiedPlaces']

        res = {}

        cluster_info = {
            'Занято мест': len(occupied_places),
            'Всего мест': number_seats,
            'Занято в %': str(round(len(occupied_places) / number_seats * 100)) + '%'
        }

        res[cluster_name] = cluster_info
        if print_result:
            print(f'\033[1m\033[31m{cluster_name}\033[0m')
            for info_name, info_value in cluster_info.items():
                print(f'\033[1m\033[35m{info_name}\033[0m: \033[37m{info_value}\033[0m')

        return res if not print_result else None
