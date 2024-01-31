
import re
import requests
from requests.auth import HTTPBasicAuth
import copy
import openpyxl
import json

class Tester():

    def __init__(self):
        self.url_info = self.get_url_info()
        self.request_type = self.get_user_input('Please type one of the following request types: GET, POST, PUT, DELETE\n', ['GET','POST','PUT','DELETE'])
        self.authorization_method = self.get_user_input('Please type one of the following authorization methods: No Auth, Basic Auth, Bearer Token, API Key\n', ['No Auth', 'Basic Auth', 'Bearer Token', 'API Key'])
        self.authorization_data = self.get_authorization_data()
        self.main_info = self.get_main_info()

        print(self.url_info)
        print(self.request_type)
        print(self.authorization_method)
        print(self.authorization_data)
        print(self.main_info)


        self.cases = {}
        self.warning_present = False

        self.test_auth()
        self.test_headers()
        self.test_query_params()
        self.test_path_params()



        def iterate_nested_dict(dictionary):
            for key, value in dictionary.items():
                if value['data_type'] == 'j':

                    self.test_body_params(value['all_sub_params_dict'], nested_dict_key = key)
                    iterate_nested_dict(value['all_sub_params_dict'])

        self.test_body_params(self.main_info['body_params'])
        iterate_nested_dict(self.main_info['body_params'])
        
        
    
    def get_user_input(self, text, possible_values_list):

        while True:
            user_input = input(text)
            if user_input in possible_values_list:
                break
            else:
                print('Wrong input')
        
        return user_input
    
    def get_url_info(self):
        url = input('please type in the url. If the url has any input parameters in it, for example id, then just type it in the form {id}. All path parameters will be recognized automatically.\n')
        path_parameter_pattern = r'(\{[^}]*\})'
        path_parameters_list = re.findall(path_parameter_pattern, url)
        path_parameters = {}
        

        if path_parameters_list:
            print('The following path parameters have been recognized:')
            print(path_parameters_list)
            for i in path_parameters_list:
                print('Path parameter: ' + i)

                path_parameter_dict = self.get_parameter_info()

                path_parameter_dict['required'] = True

                path_parameters[i] = path_parameter_dict

                        
        return {
            'url':url,
            'path_parameters':path_parameters
        }

    

    def get_authorization_data(self):
        authorization_data = {}

        if self.authorization_method == 'Basic Auth':
            username = input('Please type your username:\n')
            password = input('Please type your password:\n')

            authorization_data['username'] = username
            authorization_data['password'] = password
        elif self.authorization_method == 'Bearer Token':
            token = input('Please type in the bearer token:\n')
            authorization_data['token'] = token
        elif self.authorization_method == 'API Key':
            key = input('Please enter the key:\n')
            value = input('Please enter the value:\n')
            add_to = self.get_user_input('Where do you want to add the API Key? Options: Header, Query Params\n', ['Header', 'Query Params'])

            authorization_data['key'] = key
            authorization_data['value'] = value
            authorization_data['add_to'] = add_to
        else:
            pass

        return authorization_data
    

    def get_main_info(self):

        # QUERY PARAMETERS

        query_params = {}

        while True:
            new_query_param = self.get_user_input('Do you want to add new query parameter? Type 0 for No and 1 for yes\n', ['0','1'])
            if new_query_param == '0':
                break
            else:
                query_param_name = input('Please type the query parameter name:\n')
                query_param_dict = self.get_parameter_info()

                query_params[query_param_name] = query_param_dict

        print('Thank you for adding all query parameters')


        #HEADERS

        headers = {}


        while True:
            new_header = self.get_user_input('Do you want to add new header? Type 0 for No and 1 for yes\n', ['0','1'])
            if new_header == '0':
                break
            else:
                header_name = input('Please type the header name:\n')
                header_dict = self.get_parameter_info()



                headers[header_name] = header_dict

        print('Thank you for adding all headers')


        # REQUEST BODY PARAMETERS   

        body_params = {}

        while True:
            new_body_param = self.get_user_input('Do you want to add new request body parameter? Type 0 for No and 1 for yes\n', ['0','1'])
            if new_body_param == '0':
                break
            else:
                body_param_name = input('Please type the body parameter name:\n')
                body_param_dict = self.get_parameter_info()



                body_params[body_param_name] = body_param_dict


        print('Thank you for adding all request body parameters')



        

        return {
            'query_params':query_params,
            'headers':headers,
            'body_params':body_params
        
        }
    

    
    def get_parameter_info(self):
        parameter_info = {}

        required = self.get_user_input('Is the parameter required? Type 0 for No, 1 for Yes\n', ['0', '1'])

        if required == '0':
            required = False
        else:
            required = True
        



        data_type = self.get_user_input('Is the parameter a string, integer or float? Type s for string, i for integer, f for float, j for json\n', ['s', 'i', 'f', 'j'])

        ###
        if data_type == 'j':
            print('this param is in json format. Please enter data for this json')

            json_params = {}

            while True:
                new_body_param = self.get_user_input('Do you want to add new request body parameter? Type 0 for No and 1 for yes\n', ['0','1'])
                if new_body_param == '0':
                    break
                else:
                    body_param_name = input('Please type the body parameter name:\n')
                    body_param_dict = self.get_parameter_info()



                    json_params[body_param_name] = body_param_dict
            

            print('Thank you for adding all parameters for this json')

            parameter_info['all_sub_params_dict'] = json_params
        ###



        string_max_length = None
        if data_type == 's':
            has_max_val = self.get_user_input('Does this string have a maximum length? 0 for No, 1 for Yes\n', ['0','1'])
        
            if has_max_val == '1':
                while True:
                    try:
                        string_max_length = int(input('Please enter the maximum length:\n'))
                        break
                    except:
                        print('Wrong data type. Please try again')
        
        string_min_length = None
        if data_type == 's':
            has_min_val = self.get_user_input('Does this string have a minimum length? 0 for No, 1 for Yes\n', ['0','1'])
        
            if has_min_val == '1':
                while True:
                    try:
                        string_min_length = int(input('Please enter the minimum length:\n'))
                        break
                    except:
                        print('Wrong data type. Please try again')

                        

        value_range = []

        if data_type != 'j':

            has_value_range = self.get_user_input('Does this parameter have a limited value range? Write 0 for No and 1 for Yes\n', ['0','1'])

            if has_value_range == '1':
                is_continious_range = self.get_user_input('Is it a continious range? Write 0 for No and 1 for Yes\n', ['0','1'])

                if is_continious_range == '1':
                    while True:
                        try:
                            starting_val = int(input('Please enter the starting value. Must be an integer\n'))
                            final_val = int(input('Please enter the final value. Must be an integer\n'))
                            step = int(input('Please enter the step. Must be an integer\n'))


                            ###
                            if final_val > starting_val and step > 0:
                                if data_type != 's':
                                    break
                                else:                   
                                    cond2 = False
                                    error2 = 'Final value string length must be less than or equal to maximum string length'

                                    if string_max_length:
                                        if len(str(final_val)) <= string_max_length:
                                            cond2 = True
                                    else:
                                        cond2 = True
                                    
                                    cond3 = False
                                    error3 = 'Starting value string length must be greater than or equal to minimum string length'

                                    if string_min_length:
                                        if len(str(starting_val)) >= string_min_length:
                                            cond3 = True
                                    else:
                                        cond3 = True

                                    if not cond2:
                                        print(error2)
                                    elif not cond3:
                                        print(error3)
                                    else:
                                        break
                                    
                            else:
                                print('Error. Please check that the final value is greater than starting value and that the step is greater than 0')
                                
                        except:
                            print('Wrong data types provided. Try again')
                    
                    for i in range(starting_val, final_val+1, step):

                        if data_type == 's':
                            value_range.append(str(i))
                        else:
                            value_range.append(i)

                else:
                    while True:
                        ###
                        value = input('Please enter the value. Type __STOP__ if you want to stop.\n')

                        if value == '__STOP__':
                            break

                        if data_type == 'i':
                            try:
                                value = int(value)
                            except:
                                print('Value is not integer while the data type is. Please try again')
                                continue
                        
                        elif data_type == 'f':
                            try:
                                value = float(value)
                            except:
                                print('Value is not float while the data type is. Please try again')
                                continue
                        elif data_type == 's':
                            if string_max_length:
                                if len(value) > string_max_length:
                                    print('String length must be smaller than or equal to maximum length')
                                    continue
                            if string_min_length:
                                if len(value) < string_min_length:
                                    print('String length must be greater than or equal to minimum length')
                                    continue

                                

                        
                        value_range.append(value)
        

        



        default_value = None

        if required:
            while True:
                ###
                try:
                    if data_type == 'i':
                        default_value = int(input('Please provide a default value for this required parameter which will form the basic request:\n'))
                    elif data_type == 'f':
                        default_value = float(input('Please provide a default value for this required parameter which will form the basic request:\n'))
                    elif data_type == 's':
                        default_value = str(input('Please provide a default value for this required parameter which will form the basic request:\n'))
                    elif data_type == 'j':
                        default_value = {}
                        for u, y in list(json_params.items()):
                            if y['required']:
                                default_value[u] = y['default_value']

                    
                    
                    cond1 = False
                    error1 = 'Default value must be in value range'

                    if value_range:
                        if default_value in value_range:
                            cond1 = True
                    else:
                        cond1 = True
                    
                    cond2 = False
                    error2 = 'Default string length must be less than or equal to maximum string length'

                    if string_max_length:
                        if len(default_value) <= string_max_length:
                            cond2 = True
                    else:
                        cond2 = True
                    
                    cond3 = False
                    error3 = 'Default string length must be greater than or equal to minimum string length'

                    if string_min_length:
                        if len(default_value) >= string_min_length:
                            cond3 = True
                    else:
                        cond3 = True


                    if not cond1:
                        print(error1)
                    elif not cond2:
                        print(error2)
                    elif not cond3:
                        print(error3)
                    else:
                        break

                except:
                    print('Wrong data type. Try again')

        
        parameter_info['required'] = required
        parameter_info['data_type'] = data_type
        parameter_info['value_range'] = value_range
        parameter_info['string_max_length'] = string_max_length
        parameter_info['string_min_length'] = string_min_length
        parameter_info['default_value'] = default_value

        return parameter_info
    

    def basic_request(self):
        url = self.url_info['url']
        path_parameters = self.url_info['path_parameters']
        headers = {"Content-Type": "application/json"}


        for i in list(path_parameters.keys()):
            if path_parameters[i]['required'] == True:
                url = url.replace(i, str(path_parameters[i]['default_value']))
        
        
        auth = None
        if self.authorization_method == 'Basic Auth':
            auth = HTTPBasicAuth(self.authorization_data['username'], self.authorization_data['password'])
        elif self.authorization_method == 'Bearer Token':
            headers['Authorization'] = f'Bearer {self.authorization_data["token"]}'
        elif self.authorization_method == 'API Key':
            if self.authorization_data['add_to'] == 'Header':
                headers[self.authorization_data["key"]] = self.authorization_data["value"]
            else:
                url = url + f'?{self.authorization_data["key"]}={self.authorization_data["value"]}'
        else:
            pass





        query_params = self.main_info['query_params']

        for n,i in enumerate([ k for k in list(query_params.keys()) if query_params[k]['required']==True ]):
            
            if n == 0:
                if '?' not in url and '=' not in url:
                    url = url + f'?{i}={query_params[i]["default_value"]}'
                else:
                    url = url + f'&{i}={query_params[i]["default_value"]}'
            else:
                url = url + f'&{i}={query_params[i]["default_value"]}'





        headers_dict = self.main_info['headers']

        for i in list(headers_dict.keys()):
            if headers_dict[i]["required"]:
                headers[i] = headers_dict[i]["default_value"]





        body_params = self.main_info['body_params']

        request_body = {}

        for i in list(body_params.keys()):
            if body_params[i]["required"]:
                request_body[i] = body_params[i]["default_value"]



        

        

        return {'url':url,
                'headers':headers,
                'auth':auth,
                'request_body':request_body}
    



    def test_auth(self):
        basic_request_info = self.basic_request()
        url = basic_request_info['url']
        auth = basic_request_info['auth']
        headers = copy.deepcopy(basic_request_info['headers'])
        request_body = copy.deepcopy(basic_request_info['request_body'])


        #Testing no Auth
        if self.authorization_method == 'Bearer Token':
            headers.pop('Authorization')
        elif self.authorization_method == 'API Key':
            if self.authorization_data['add_to'] == 'Header':
                headers.pop(self.authorization_data["key"])
            else:
                pattern = r'([?&]{}=)[^&]+(&|$)'.format(self.authorization_data["key"])
                replacement = r'\1TEMPORARYREPLACEMENT{}\2'.format('')
                url = re.sub(pattern, replacement, url)
                url = url.replace('TEMPORARYREPLACEMENT','')

                if f'?{self.authorization_data["key"]}=' in url:
                    if url.endswith(f'?{self.authorization_data["key"]}='):
                        url = url.replace(f'?{self.authorization_data["key"]}=', '')
                    else:
                        url = url.replace(f'{self.authorization_data["key"]}=&','')
                else:
                    url = url.replace(f'&{self.authorization_data["key"]}=','')

        else:
            pass


        case_1 = {'url':url,
                  'headers':headers,
                  'request_body':request_body,
                  'auth':None,
                  'comment':'Testing no auth',
                  'expected_start_code':4}
        

        self.cases['case_1'] = case_1






        #Testing wrong Auth

        url = basic_request_info['url']
        headers = copy.deepcopy(basic_request_info['headers'])
            
        auth = None
        if self.authorization_method == 'Basic Auth':
            auth = HTTPBasicAuth('123451234554321', '123451234554321')
        elif self.authorization_method == 'Bearer Token':
            headers['Authorization'] = f'Bearer 123451234554321'
        elif self.authorization_method == 'API Key':
            if self.authorization_data['add_to'] == 'Header':
                headers[self.authorization_data["key"]] = '123451234554321'
            else:
                pattern = r'([?&]{}=)[^&]+(&|$)'.format(self.authorization_data["key"])
                replacement = r'\1TEMPORARYREPLACEMENT{}\2'.format('123451234554321')
                url = re.sub(pattern, replacement, url)
                url = url.replace('TEMPORARYREPLACEMENT','')
        else:
            pass


        case_2 = {'url':url,
                  'headers':headers,
                  'request_body':request_body,
                  'auth':auth,
                  'comment':'Testing wrong auth',
                  'expected_start_code':4}
        
        self.cases['case_2'] = case_2





        case_3 = {'url':basic_request_info['url'],
                  'headers':basic_request_info['headers'],
                  'request_body':basic_request_info['request_body'],
                  'auth':basic_request_info['auth'],
                  'comment':'Basic request',
                  'expected_start_code':2}
        


        self.cases['case_3'] = case_3

    

    def test_headers(self):
        basic_request_info = self.basic_request()
        url = basic_request_info['url']
        auth = basic_request_info['auth']
        headers = copy.deepcopy(basic_request_info['headers'])
        request_body = copy.deepcopy(basic_request_info['request_body'])

        all_headers = self.main_info['headers']





        for n,h in enumerate(list(all_headers.keys()), start=0):
            #Test if all parameters labeled as required are truly required. Trying NULL for each.
            if all_headers[h]['required']:
                headers = copy.deepcopy(basic_request_info['headers'])
                headers[h] = None
                headers.pop(h)
                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':basic_request_info['url'],
                                                    'headers':headers,
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Testing Null for required header {h}',
                                                    'expected_start_code':4}
                
            ## Testing correct values for not required parameters
            else:
                headers = copy.deepcopy(basic_request_info['headers'])
                val = None
                if all_headers[h]['value_range']:
                    val = all_headers[h]['value_range'][0]
                else:
                    if all_headers[h]['data_type'] == 's':
                        if all_headers[h]['string_min_length']:
                            val = 'a'*all_headers[h]['string_min_length']
                        else:
                            val = 'a'
                    elif all_headers[h]['data_type'] == 'i':
                        val = 12345
                    elif all_headers[h]['data_type'] == 'f':
                        val = 12345.5


                headers[h] = val
                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':basic_request_info['url'],
                                                    'headers':headers,
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Testing any correct value for non-required header {h}',
                                                    'expected_start_code':2}
        


        #If there is value range then test something outside of value range
        for n,h in enumerate(list(all_headers.keys()),start=0 ):
            headers = copy.deepcopy(basic_request_info['headers'])
            if all_headers[h]['value_range']:
                if all_headers[h]['data_type']=='s':
                    if '1234512345' not in all_headers[h]['value_range']:
                        headers[h] = '1234512345'
                    elif '123451234512072000' not in all_headers[h]['value_range']:
                        headers[h] = '123451234512072000' 
                    else:
                        self.warning_present = True
                        print('Warning!!!!')

                elif all_headers[h]['data_type']=='i':
                    if 1234512345 not in all_headers[h]['value_range']:
                        headers[h] = 1234512345
                    elif 123451234512072000 not in all_headers[h]['value_range']:
                        headers[h] = 123451234512072000 
                    else:
                        self.warning_present = True
                        print('Warning!!!!')

                elif all_headers[h]['data_type'] == 'f':
                    if 1234512345.5 not in all_headers[h]['value_range']:
                        headers[h] = 1234512345.5
                    elif 123451234512072000.5 not in all_headers[h]['value_range']:
                        headers[h] = 123451234512072000.5
                    else:
                        self.warning_present = True
                        print('Warning!!!!')
                
                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':basic_request_info['url'],
                                                'headers':headers,
                                                'request_body':basic_request_info['request_body'],
                                                'auth':basic_request_info['auth'],
                                                'comment':f'Header: {h}. Testing value out of value range',
                                                'expected_start_code':4}
            
                    



        for n,h in enumerate(list(all_headers.keys()),start=0 ):
            headers = copy.deepcopy(basic_request_info['headers'])
            #If string then test for max limit if there is one
            if all_headers[h]['data_type']=='s':
                if all_headers[h]['string_max_length']:
                    headers[h] = 'aa'*all_headers[h]['string_max_length']

                    self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':basic_request_info['url'],
                                            'headers':headers,
                                            'request_body':basic_request_info['request_body'],
                                            'auth':basic_request_info['auth'],
                                            'comment':f'Header: {h}. Testing max string length. Expected value: {all_headers[h]["string_max_length"]}',
                                            'expected_start_code':4}


            #If integer or float then test string
            else:
                headers[h] = '12345aaa'
                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':basic_request_info['url'],
                                            'headers':headers,
                                            'request_body':basic_request_info['request_body'],
                                            'auth':basic_request_info['auth'],
                                            'comment': f'Header: {h}. Testing string for integer or float',
                                            'expected_start_code':4}
                    
        

        for n,h in enumerate(list(all_headers.keys()),start=0 ):
            headers = copy.deepcopy(basic_request_info['headers'])
            #If string then test for min limit if there is one
            if all_headers[h]['data_type']=='s':
                if all_headers[h]['string_min_length']:

                    if all_headers[h]['string_min_length'] > 1:
                        headers[h] = 'a'

                        self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':basic_request_info['url'],
                                                'headers':headers,
                                                'request_body':basic_request_info['request_body'],
                                                'auth':basic_request_info['auth'],
                                                'comment':f'Header: {h}. Testing min string length. Expected value: {all_headers[h]["string_min_length"]}',
                                                'expected_start_code':4}
                    else:
                        headers[h] = ''

                        self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':basic_request_info['url'],
                                                'headers':headers,
                                                'request_body':basic_request_info['request_body'],
                                                'auth':basic_request_info['auth'],
                                                'comment':f'Header: {h}. Testing min string length. Expected value: {all_headers[h]["string_min_length"]}',
                                                'expected_start_code':4}
                        


        ##Testing last val from value range
        for n,h in enumerate(list(all_headers.keys()),start=0):
            if all_headers[h]['value_range']:
                headers = copy.deepcopy(basic_request_info['headers'])
                headers[h] = all_headers[h]['value_range'][-1]
                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':basic_request_info['url'],
                                                    'headers':headers,
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Header: {h}. Testing last value from value range',
                                                    'expected_start_code':2}
                

        


                



                        

    




    def test_body_params(self, dictionary, nested_dict_key=None):
        basic_request_info = self.basic_request()
        url = basic_request_info['url']
        auth = basic_request_info['auth']
        headers = copy.deepcopy(basic_request_info['headers'])
        request_body = copy.deepcopy(basic_request_info['request_body'])

        all_body_params = dictionary



        def basic_request_body_looper(basic_request_body, nested_dict_key, key_inside_nested_dict, value):

            for main_key, main_value in basic_request_body.items():
                if main_key == nested_dict_key and isinstance(main_value, dict):
                    main_value[key_inside_nested_dict] = value

                    if value == None:
                        main_value.pop(key_inside_nested_dict)
                    break
                    
                elif isinstance(main_value, dict):
                    basic_request_body_looper(main_value, nested_dict_key, key_inside_nested_dict, value)


        def basic_request_body_modifier(basic_request_body, nested_dict_key, key_inside_nested_dict, value):
            if nested_dict_key:
                basic_request_body_looper(basic_request_body, nested_dict_key, key_inside_nested_dict, value)
            else:
                basic_request_body[key_inside_nested_dict] = value

                if value == None:
                    basic_request_body.pop(key_inside_nested_dict)
            
            return basic_request_body
        



                    


                    



            





        




        for n,h in enumerate(list(all_body_params.keys()),start=0):
            #Test if all parameters labeled as required are truly required. Trying NULL for each.
            if all_body_params[h]['required']:

                request_body = basic_request_body_modifier(copy.deepcopy(basic_request_info['request_body']), nested_dict_key, h, None)

                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':basic_request_info['url'],
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':request_body,
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Testing Null for required body param {h}',
                                                    'expected_start_code':4}
                
            ## Testing correct values for not required parameters
            else:

                def find_default_val_json(json_key_val):
                    default_val_json = {}
                    for p in list(json_key_val.keys()):
                        if json_key_val[p]['value_range']:
                            val_in_json = json_key_val[p]['value_range'][0]
                        else:
                            if json_key_val[p]['data_type'] == 's':
                                if json_key_val[p]['string_min_length']:
                                    val_in_json = 'a'*json_key_val[p]['string_min_length']
                                else:
                                    val_in_json = 'a'
                            elif json_key_val[p]['data_type'] == 'i':
                                val_in_json = 12345
                            elif json_key_val[p]['data_type'] == 'f':
                                val_in_json = 12345.5
                            elif json_key_val[p]['data_type'] == 'j':
                                val_in_json = find_default_val_json(json_key_val[p]['all_sub_params_dict'])
                        
                        default_val_json[p] = val_in_json
                    return default_val_json

                val = None
                if all_body_params[h]['value_range']:
                    val = all_body_params[h]['value_range'][0]
                else:
                    if all_body_params[h]['data_type'] == 's':
                        if all_body_params[h]['string_min_length']:
                            val = 'a'*all_body_params[h]['string_min_length']
                        else:
                            val = 'a'
                    elif all_body_params[h]['data_type'] == 'i':
                        val = 12345
                    elif all_body_params[h]['data_type'] == 'f':
                        val = 12345.5
                    elif all_body_params[h]['data_type'] == 'j':
                        val = find_default_val_json(all_body_params[h]['all_sub_params_dict'])
                        





                request_body = basic_request_body_modifier(copy.deepcopy(basic_request_info['request_body']), nested_dict_key, h, val)

                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':basic_request_info['url'],
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':request_body,
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Testing any correct value for non-required body param {h}',
                                                    'expected_start_code':2}
        







        #If there is value range then test something outside of value range
        for n,h in enumerate(list(all_body_params.keys()),start=0 ):

            if all_body_params[h]['value_range']:
                val = None
                if all_body_params[h]['data_type']=='s':
                    if '1234512345' not in all_body_params[h]['value_range']:
                        val = '1234512345'

                    elif '123451234512072000' not in all_body_params[h]['value_range']:
                        val = '123451234512072000' 
                    else:
                        self.warning_present = True
                        print('Warning!!!!')

                elif all_body_params[h]['data_type']=='i':
                    if 1234512345 not in all_body_params[h]['value_range']:
                        val = 1234512345
                    elif 123451234512072000 not in all_body_params[h]['value_range']:
                        val = 123451234512072000 
                    else:
                        self.warning_present = True
                        print('Warning!!!!')

                elif all_body_params[h]['data_type']=='f':
                    if 1234512345.5 not in all_body_params[h]['value_range']:
                        val = 1234512345.5
                    elif 123451234512072000.5 not in all_body_params[h]['value_range']:
                        val = 123451234512072000.5
                    else:
                        self.warning_present = True
                        print('Warning!!!!')
                
                request_body = basic_request_body_modifier(copy.deepcopy(basic_request_info['request_body']), nested_dict_key, h, val)

                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':basic_request_info['url'],
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':request_body,
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Body param: {h}. Testing value out of value range',
                                                    'expected_start_code':4}
            
                    



        for n,h in enumerate(list(all_body_params.keys()),start=0 ):

            #If string then test for max limit if there is one
            if all_body_params[h]['data_type']=='s':
                if all_body_params[h]['string_max_length']:

                    request_body = basic_request_body_modifier(copy.deepcopy(basic_request_info['request_body']), nested_dict_key, h, 'aa'*all_body_params[h]['string_max_length'])

                    self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':basic_request_info['url'],
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':request_body,
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Body param: {h}. Testing max string length. Expected value: {all_body_params[h]["string_max_length"]}',
                                                    'expected_start_code':4}


            #If integer or float then test string
            else:

                request_body = basic_request_body_modifier(copy.deepcopy(basic_request_info['request_body']), nested_dict_key, h, '12345aaa')
                
                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':basic_request_info['url'],
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':request_body,
                                                    'auth':basic_request_info['auth'],
                                                    'comment': f'Body param: {h}. Testing string for integer or float or json',
                                                    'expected_start_code':4}
                    
        

        for n,h in enumerate(list(all_body_params.keys()),start=0 ):

            #If string then test for min limit if there is one
            if all_body_params[h]['data_type']=='s':
                if all_body_params[h]['string_min_length']:

                    if all_body_params[h]['string_min_length'] > 1:

                        request_body = basic_request_body_modifier(copy.deepcopy(basic_request_info['request_body']), nested_dict_key, h, 'a')

                        
                        self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':basic_request_info['url'],
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':request_body,
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Body param: {h}. Testing min string length. Expected value: {all_body_params[h]["string_min_length"]}',
                                                    'expected_start_code':4}
                    else:

                        request_body = basic_request_body_modifier(copy.deepcopy(basic_request_info['request_body']), nested_dict_key, h, '')

                        self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':basic_request_info['url'],
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':request_body,
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Body param: {h}. Testing min string length. Expected value: {all_body_params[h]["string_min_length"]}',
                                                    'expected_start_code':4}
                        

        ##Testing last val from value range
        for n,h in enumerate(list(all_body_params.keys()),start=0):
            if all_body_params[h]['value_range']:

                request_body = basic_request_body_modifier(copy.deepcopy(basic_request_info['request_body']), nested_dict_key, h, all_body_params[h]['value_range'][-1])

                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':basic_request_info['url'],
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':request_body,
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Body param: {h}. Testing last value from value range',
                                                    'expected_start_code':2}
                        




    def test_query_params(self):
        basic_request_info = self.basic_request()
        url = basic_request_info['url']
        auth = basic_request_info['auth']
        headers = copy.deepcopy(basic_request_info['headers'])
        request_body = copy.deepcopy(basic_request_info['request_body'])

        all_query_params = self.main_info['query_params']


        for n,h in enumerate(list(all_query_params.keys()),start=0):
            #Test if all parameters labeled as required are truly required. Trying NULL for each.
            ##+
            if all_query_params[h]['required']:
                url = basic_request_info['url']

                pattern = r'([?&]{}=)[^&]+(&|$)'.format(h)
                replacement = r'\1TEMPORARYREPLACEMENT{}\2'.format('')
                url = re.sub(pattern, replacement, url)
                url = url.replace('TEMPORARYREPLACEMENT','')

                if f'?{h}=' in url:
                    if url.endswith(f'?{h}='):
                        url = url.replace(f'?{h}=', '')
                    else:
                        url = url.replace(f'{h}=&','')
                else:
                    url = url.replace(f'&{h}=','')


                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':url,
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Testing Null for required query param {h}',
                                                    'expected_start_code':4}
                
            ## Testing correct values for not required parameters
            ##+
            else:
                url = basic_request_info['url']
                val = None
                if all_query_params[h]['value_range']:
                    val = all_query_params[h]['value_range'][0]
                else:
                    if all_query_params[h]['data_type'] == 's':
                        if all_query_params[h]['string_min_length']:
                            val = 'a'*all_query_params[h]['string_min_length']
                        else:
                            val = 'a'
                    elif all_query_params[h]['data_type'] == 'i':
                        val = 12345
                    elif all_query_params[h]['data_type'] == 'f':
                        val = 12345.5



                if '?' in url and '=' in url:
                    url += f'&{h}={val}'
                else:
                    url += f'?{h}={val}'


                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':url,
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Testing any correct value for non-required query param {h}',
                                                    'expected_start_code':2}
        


        #If there is value range then test something outside of value range
        ##+
        for n,h in enumerate(list(all_query_params.keys()),start=0 ):
            url = basic_request_info['url']
            if all_query_params[h]['value_range']:
                if all_query_params[h]['data_type']=='s':
                    if '1234512345' not in all_query_params[h]['value_range']:
                        val = '1234512345'
                        
                        if all_query_params[h]['required']:
                            pattern = r'([?&]{}=)[^&]+(&|$)'.format(h)
                            replacement = r'\1TEMPORARYREPLACEMENT{}\2'.format(val)
                            url = re.sub(pattern, replacement, url)
                            url = url.replace('TEMPORARYREPLACEMENT','')
                        else:
                            if '?' in url and '=' in url:
                                url += f'&{h}={val}'
                            else:
                                url += f'?{h}={val}'



                    elif '123451234512072000' not in all_query_params[h]['value_range']:

                        val = '123451234512072000'

                        if all_query_params[h]['required']:
                            pattern = r'([?&]{}=)[^&]+(&|$)'.format(h)
                            replacement = r'\1TEMPORARYREPLACEMENT{}\2'.format(val)
                            url = re.sub(pattern, replacement, url)
                            url = url.replace('TEMPORARYREPLACEMENT','')
                        else:
                            if '?' in url and '=' in url:
                                url += f'&{h}={val}'
                            else:
                                url += f'?{h}={val}'


                    else:
                        self.warning_present = True
                        print('Warning!!!!')

                elif all_query_params[h]['data_type']=='i':
                    if 1234512345 not in all_query_params[h]['value_range']:
                        val = 1234512345
                        if all_query_params[h]['required']:
                            pattern = r'([?&]{}=)[^&]+(&|$)'.format(h)
                            replacement = r'\1TEMPORARYREPLACEMENT{}\2'.format(val)
                            url = re.sub(pattern, replacement, url)
                            url = url.replace('TEMPORARYREPLACEMENT','')
                        else:
                            if '?' in url and '=' in url:
                                url += f'&{h}={val}'
                            else:
                                url += f'?{h}={val}'

                    elif 123451234512072000 not in all_query_params[h]['value_range']: 
                        val = 123451234512072000
                        if all_query_params[h]['required']:
                            pattern = r'([?&]{}=)[^&]+(&|$)'.format(h)
                            replacement = r'\1TEMPORARYREPLACEMENT{}\2'.format(val)
                            url = re.sub(pattern, replacement, url)
                            url = url.replace('TEMPORARYREPLACEMENT','')
                        else:
                            if '?' in url and '=' in url:
                                url += f'&{h}={val}'
                            else:
                                url += f'?{h}={val}'

                    else:
                        self.warning_present = True
                        print('Warning!!!!')

                elif all_query_params[h]['data_type']=='f':
                    if 1234512345.5 not in all_query_params[h]['value_range']:
                        val = 1234512345.5

                        if all_query_params[h]['required']:
                            pattern = r'([?&]{}=)[^&]+(&|$)'.format(h)
                            replacement = r'\1TEMPORARYREPLACEMENT{}\2'.format(val)
                            url = re.sub(pattern, replacement, url)
                            url = url.replace('TEMPORARYREPLACEMENT','')
                        else:
                            if '?' in url and '=' in url:
                                url += f'&{h}={val}'
                            else:
                                url += f'?{h}={val}'


                    elif 123451234512072000.5 not in all_query_params[h]['value_range']:
                        val = 123451234512072000.5
                        if all_query_params[h]['required']:
                            pattern = r'([?&]{}=)[^&]+(&|$)'.format(h)
                            replacement = r'\1TEMPORARYREPLACEMENT{}\2'.format(val)
                            url = re.sub(pattern, replacement, url)
                            url = url.replace('TEMPORARYREPLACEMENT','')
                        else:
                            if '?' in url and '=' in url:
                                url += f'&{h}={val}'
                            else:
                                url += f'?{h}={val}'

                    else:
                        self.warning_present = True
                        print('Warning!!!!')
                
                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':url,
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Query param: {h}. Testing value out of value range',
                                                    'expected_start_code':4}
            
                    



        for n,h in enumerate(list(all_query_params.keys()),start=0 ):
            url = basic_request_info['url']
            #If string then test for max limit if there is one
            if all_query_params[h]['data_type']=='s':
                if all_query_params[h]['string_max_length']:
                    val = 'aa'*all_query_params[h]['string_max_length']
                    if all_query_params[h]['required']:
                        pattern = r'([?&]{}=)[^&]+(&|$)'.format(h)
                        replacement = r'\1TEMPORARYREPLACEMENT{}\2'.format(val)
                        url = re.sub(pattern, replacement, url)
                        url = url.replace('TEMPORARYREPLACEMENT','')
                    else:
                        if '?' in url and '=' in url:
                            url += f'&{h}={val}'
                        else:
                            url += f'?{h}={val}'


                    self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':url,
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Query param: {h}. Testing max string length. Expected value: {all_query_params[h]["string_max_length"]}',
                                                    'expected_start_code':4}


            #If integer or float then test string
            else:
                val = '12345aaa'
                if all_query_params[h]['required']:
                    pattern = r'([?&]{}=)[^&]+(&|$)'.format(h)
                    replacement = r'\1TEMPORARYREPLACEMENT{}\2'.format(val)
                    url = re.sub(pattern, replacement, url)
                    url = url.replace('TEMPORARYREPLACEMENT','')
                else:
                    if '?' in url and '=' in url:
                        url += f'&{h}={val}'
                    else:
                        url += f'?{h}={val}'


                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':url,
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment': f'Query param: {h}. Testing string for integer or float',
                                                    'expected_start_code':4}
                    
        

        for n,h in enumerate(list(all_query_params.keys()),start=0 ):
            url = basic_request_info['url']
            #If string then test for min limit if there is one
            if all_query_params[h]['data_type']=='s':
                if all_query_params[h]['string_min_length']:

                    if all_query_params[h]['string_min_length'] > 1:

                        val = 'a'

                        if all_query_params[h]['required']:
                            pattern = r'([?&]{}=)[^&]+(&|$)'.format(h)
                            replacement = r'\1TEMPORARYREPLACEMENT{}\2'.format(val)
                            url = re.sub(pattern, replacement, url)
                            url = url.replace('TEMPORARYREPLACEMENT','')
                        else:
                            if '?' in url and '=' in url:
                                url += f'&{h}={val}'
                            else:
                                url += f'?{h}={val}'

                        self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':url,
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Query param: {h}. Testing min string length. Expected value: {all_query_params[h]["string_min_length"]}',
                                                    'expected_start_code':4}
                    else:

                        val = ''

                        if all_query_params[h]['required']:
                            pattern = r'([?&]{}=)[^&]+(&|$)'.format(h)
                            replacement = r'\1TEMPORARYREPLACEMENT{}\2'.format(val)
                            url = re.sub(pattern, replacement, url)
                            url = url.replace('TEMPORARYREPLACEMENT','')
                        else:
                            if '?' in url and '=' in url:
                                url += f'&{h}={val}'
                            else:
                                url += f'?{h}={val}'


                        self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':url,
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Query param: {h}. Testing min string length. Expected value: {all_query_params[h]["string_min_length"]}',
                                                    'expected_start_code':4}
                        

        ##Testing last val from value range
        for n,h in enumerate(list(all_query_params.keys()),start=0):
            if all_query_params[h]['value_range']:
                url = basic_request_info['url']

                val = all_query_params[h]['value_range'][-1]

                if all_query_params[h]['required']:
                    pattern = r'([?&]{}=)[^&]+(&|$)'.format(h)
                    replacement = r'\1TEMPORARYREPLACEMENT{}\2'.format(val)
                    url = re.sub(pattern, replacement, url)
                    url = url.replace('TEMPORARYREPLACEMENT','')
                else:
                    if '?' in url and '=' in url:
                        url += f'&{h}={val}'
                    else:
                        url += f'?{h}={val}'


                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':url,
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Query param: {h}. Testing last value from value range',
                                                    'expected_start_code':2}












    def test_path_params(self):
        basic_request_info = self.basic_request()
        url = basic_request_info['url']
        auth = basic_request_info['auth']
        headers = copy.deepcopy(basic_request_info['headers'])
        request_body = copy.deepcopy(basic_request_info['request_body'])

        all_path_parameters = self.url_info['path_parameters']

        #If there is value range then test something outside of value range
        for n,h in enumerate(list(all_path_parameters.keys()),start=0 ):
            if all_path_parameters[h]['value_range']:
                val = None
                ##+
                if all_path_parameters[h]['data_type']=='s':
                    if '1234512345' not in all_path_parameters[h]['value_range']:
                        val = '1234512345'

                        url = self.url_info['url']
                        for i in list(all_path_parameters.keys()):
                            if i!=h:
                                url = url.replace(i, str(all_path_parameters[i]['default_value']))
                            else:
                                url = url.replace(i, val)

                    elif '123451234512072000' not in all_path_parameters[h]['value_range']:

                        val = '123451234512072000'

                        url = self.url_info['url']
                        for i in list(all_path_parameters.keys()):
                            if i!=h:
                                url = url.replace(i, str(all_path_parameters[i]['default_value']))
                            else:
                                url = url.replace(i, val)

                    else:
                        self.warning_present = True
                        print('Warning!!!!')

                ##+
                elif all_path_parameters[h]['data_type']=='i':
                    
                    if 1234512345 not in all_path_parameters[h]['value_range']:

                        val = 1234512345

                        url = self.url_info['url']
                        for i in list(all_path_parameters.keys()):
                            if i!=h:
                                url = url.replace(i, str(all_path_parameters[i]['default_value']))
                            else:
                                url = url.replace(i, str(val))

                    elif 123451234512072000 not in all_path_parameters[h]['value_range']:

                        val = 123451234512072000

                        url = self.url_info['url']
                        for i in list(all_path_parameters.keys()):
                            if i!=h:
                                url = url.replace(i, str(all_path_parameters[i]['default_value']))
                            else:
                                url = url.replace(i, str(val))

                    else:
                        self.warning_present = True
                        print('Warning!!!!')
                ##-
                elif all_path_parameters[h]['data_type']=='f':
                    if 1234512345.5 not in all_path_parameters[h]['value_range']:

                        val = 1234512345.5

                        url = self.url_info['url']
                        for i in list(all_path_parameters.keys()):
                            if i!=h:
                                url = url.replace(i, str(all_path_parameters[i]['default_value']))
                            else:
                                url = url.replace(i, str(val))

                    elif 123451234512072000.5 not in all_path_parameters[h]['value_range']:

                        val = 123451234512072000.5

                        url = self.url_info['url']
                        for i in list(all_path_parameters.keys()):
                            if i!=h:
                                url = url.replace(i, str(all_path_parameters[i]['default_value']))
                            else:
                                url = url.replace(i, str(val))
                            
                    else:
                        self.warning_present = True
                        print('Warning!!!!')
                
                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':url,
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Path param: {h}. Testing value out of value range',
                                                    'different_path_params':{'key':h,
                                                                             'value':val},
                                                    'expected_start_code':4}
            
                    



        for n,h in enumerate(list(all_path_parameters.keys()),start=0 ):

            #If string then test for max limit if there is one
            if all_path_parameters[h]['data_type']=='s':
                ##+
                if all_path_parameters[h]['string_max_length']:

                    url = self.url_info['url']
                    for i in list(all_path_parameters.keys()):
                        if i!=h:
                            url = url.replace(i, str(all_path_parameters[i]['default_value']))
                        else:
                            url = url.replace(i, 'aa'*all_path_parameters[h]['string_max_length'])

                    self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':url,
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Path param: {h}. Testing max string length. Expected value: {all_path_parameters[h]["string_max_length"]}',
                                                    'different_path_params':{'key':h,
                                                                             'value':'aa'*all_path_parameters[h]['string_max_length']},
                                                    'expected_start_code':4}


            #If integer or float then test string
            ##+
            else:

                url = self.url_info['url']
                for i in list(all_path_parameters.keys()):
                    if i!=h:
                        url = url.replace(i, str(all_path_parameters[i]['default_value']))
                    else:
                        url = url.replace(i, '12345aaa')

                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':url,
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment': f'Path param: {h}. Testing string for integer or float',
                                                    'different_path_params':{'key':h,
                                                                             'value':'12345aaa'},
                                                    'expected_start_code':4}
                    
        

        for n,h in enumerate(list(all_path_parameters.keys()),start=0 ):

            #If string then test for min limit if there is one
            ##+
            if all_path_parameters[h]['data_type']=='s':
                if all_path_parameters[h]['string_min_length']:

                    if all_path_parameters[h]['string_min_length'] > 1:

                        url = self.url_info['url']
                        for i in list(all_path_parameters.keys()):
                            if i!=h:
                                url = url.replace(i, str(all_path_parameters[i]['default_value']))
                            else:
                                url = url.replace(i, 'a')

                        self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':url,
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Path param: {h}. Testing min string length. Expected value: {all_path_parameters[h]["string_min_length"]}',
                                                    'different_path_params':{'key':h,
                                                                             'value':'a'},
                                                    'expected_start_code':4}
                    else:

                        url = self.url_info['url']
                        for i in list(all_path_parameters.keys()):
                            if i!=h:
                                url = url.replace(i, str(all_path_parameters[i]['default_value']))
                            else:
                                url = url.replace(i, '')

                        self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':url,
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Path param: {h}. Testing min string length. Expected value: {all_path_parameters[h]["string_min_length"]}',
                                                    'different_path_params':{'key':h,
                                                                             'value':''},
                                                    'expected_start_code':4}
    


        ##Testing last val from value range
        ##+
        for n,h in enumerate(list(all_path_parameters.keys()),start=0):
            if all_path_parameters[h]['value_range']:

                url = self.url_info['url']
                for i in list(all_path_parameters.keys()):
                    if i!=h:
                        url = url.replace(i, str(all_path_parameters[i]['default_value']))
                    else:
                        url = url.replace(i, str(all_path_parameters[h]['value_range'][-1]))

                self.cases[f'case_{max([int(r.split("case_")[1]) for r in list(self.cases.keys())])+1}'] = {'url':url,
                                                    'headers':basic_request_info['headers'],
                                                    'request_body':basic_request_info['request_body'],
                                                    'auth':basic_request_info['auth'],
                                                    'comment':f'Path param: {h}. Testing last value from value range',
                                                    'different_path_params':{'key':h,
                                                                             'value':str(all_path_parameters[h]['value_range'][-1])},
                                                    'expected_start_code':2}
                






    def generate_excel(self):
        
        # Create a new Excel workbook
        workbook = openpyxl.Workbook()

        # Get the active sheet (default sheet created with the workbook)
        sheet = workbook.active

        column_dict = {}

        def generate_excel_style_dict():
            alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            excel_dict = {}

            for i, char in enumerate(alphabet):
                excel_dict[i] = char

            for i, char1 in enumerate(alphabet):
                for j, char2 in enumerate(alphabet):
                    excel_dict[(i + 1) * 26 + (j + 1)-1] = char1 + char2

            return excel_dict


        def extract_param_value(param, input_string):
            pattern = r'[?&]{}=([^&$]*)(?=&|$)'.format(param)
            match = re.search(pattern, input_string)
            
            if match:
                return match.group(1)
            else:
                return None
            

        result_dict = generate_excel_style_dict()

        sheet['A1'] = 'CaseN'
        sheet['B1'] = 'Authorization'

        current_letter_index = 1

        for i in list(self.authorization_data.keys()):
            if self.authorization_method == 'API Key':
                if i != 'value' and i != 'add_to':
                    sheet[f'{result_dict[current_letter_index]}2'] = self.authorization_data[i]
                    column_dict['auth__'+i] = current_letter_index
                    current_letter_index += 1
                    
            else:
                sheet[f'{result_dict[current_letter_index]}2'] = i
                column_dict['auth__'+i] = current_letter_index
                current_letter_index += 1

        sheet[f'{result_dict[current_letter_index]}1'] = 'Headers'
                
        for i in list(self.main_info['headers'].keys()):
            sheet[f'{result_dict[current_letter_index]}2'] = i
            column_dict['headers__'+i] = current_letter_index
            current_letter_index += 1

            
        sheet[f'{result_dict[current_letter_index]}1'] = 'Request body parameters'
                
        for i in list(self.main_info['body_params'].keys()):
            sheet[f'{result_dict[current_letter_index]}2'] = i
            column_dict['request_body__'+i] = current_letter_index
            current_letter_index += 1


        sheet[f'{result_dict[current_letter_index]}1'] = 'Query parameters'
                
        for i in list(self.main_info['query_params'].keys()):
            sheet[f'{result_dict[current_letter_index]}2'] = i
            column_dict['query_params__'+i] = current_letter_index
            current_letter_index += 1
            

        sheet[f'{result_dict[current_letter_index]}1'] = 'Path parameters'
                
        for i in list(self.url_info['path_parameters'].keys()):
            sheet[f'{result_dict[current_letter_index]}2'] = i
            column_dict['path_parameters__' + i] = current_letter_index
            current_letter_index += 1

            
        sheet[f'{result_dict[current_letter_index]}1'] = 'Test related comment'
        test_related_comment_index = current_letter_index

        current_letter_index += 1

        sheet[f'{result_dict[current_letter_index]}1'] = 'Expected results'
        sheet[f'{result_dict[current_letter_index]}2'] = 'response code'

        column_dict['expected_results__response_code'] = current_letter_index

        current_letter_index += 1

        sheet[f'{result_dict[current_letter_index]}1'] = 'Actual results'
        sheet[f'{result_dict[current_letter_index]}2'] = 'response code'

        column_dict['actual_results__response_code'] = current_letter_index

        current_letter_index += 1

        sheet[f'{result_dict[current_letter_index]}2'] = 'response body'

        column_dict['actual_results__response_body'] = current_letter_index


        current_letter_index += 1
        sheet[f'{result_dict[current_letter_index]}1'] = 'Test passed'
        column_dict['test_passed'] = current_letter_index

            
            
        for i in list(self.cases.keys()):
            case_num = i.split('case_')[1]
            level = int(case_num) + 2
            
            sheet[f'A{level}'] = case_num
            
            
            if self.authorization_method == 'Basic Auth':
                try:
                    sheet[f'{result_dict[column_dict["auth__username"]]}{level}'] = self.cases[i]['auth'].username
                    sheet[f'{result_dict[column_dict["auth__password"]]}{level}'] = self.cases[i]['auth'].password
                except:
                    sheet[f'{result_dict[column_dict["auth__username"]]}{level}'] = 'NULL'
                    sheet[f'{result_dict[column_dict["auth__password"]]}{level}'] = 'NULL'
                    

            elif self.authorization_method == 'Bearer Token':
                try:
                    sheet[f'{result_dict[column_dict["auth__token"]]}{level}'] = self.cases[i]['headers']['Authorization'].split('Bearer ')[1]
                except KeyError:
                    sheet[f'{result_dict[column_dict["auth__token"]]}{level}'] = 'NULL'
                
            elif self.authorization_method == 'API Key':
                try:
                    sheet[f'{result_dict[column_dict["auth__key"]]}{level}'] = self.cases[i]['headers'][self.authorization_data['key']]
                except KeyError:
                    sheet[f'{result_dict[column_dict["auth__key"]]}{level}'] = 'NULL'
            else:
                pass
            
            
            for h in list(self.main_info['headers'].keys()):
                try:
                    sheet[f'{result_dict[column_dict["headers__" + h]]}{level}'] = self.cases[i]['headers'][h]
                        
                except KeyError:
                    sheet[f'{result_dict[column_dict["headers__" + h]]}{level}'] = 'NULL'
                
            for h in list(self.main_info['body_params'].keys()):
                try:
                    sheet[f'{result_dict[column_dict["request_body__" + h]]}{level}'] = str(self.cases[i]['request_body'][h])
                except KeyError:
                    sheet[f'{result_dict[column_dict["request_body__" + h]]}{level}'] = 'NULL'
            
            
            
            for h in list(self.main_info['query_params'].keys()):
                sheet[f'{result_dict[column_dict["query_params__" + h]]}{level}'] = 'NULL'
                val = extract_param_value(h, self.cases[i]['url'])
                if val:
                    sheet[f'{result_dict[column_dict["query_params__" + h]]}{level}'] = val
                
            
            
            for h in list(self.url_info['path_parameters'].keys()):
                
                try:
                    different_path_param = self.cases[i]['different_path_params']
                    
                    
                    
                    if h != different_path_param['key']:
                        
                        sheet[f'{result_dict[column_dict["path_parameters__" + h]]}{level}'] = self.url_info['path_parameters'][h]['default_value']
                    
                    else:
                        sheet[f'{result_dict[column_dict["path_parameters__" + h]]}{level}'] = different_path_param['value']
                        

                except KeyError:
                    sheet[f'{result_dict[column_dict["path_parameters__" + h]]}{level}'] = self.url_info['path_parameters'][h]['default_value']
            
            
            sheet[f'{result_dict[test_related_comment_index]}{level}'] = self.cases[i]['comment']

            sheet[f'{result_dict[column_dict["expected_results__response_code"]]}{level}'] = self.cases[i]['expected_start_code']

        
            
        
        self.index_letter_dict = result_dict
        self.param_index_dict = column_dict


        # Save the workbook to a file
        workbook.save('TestCases.xlsx')







    def test_cases(self):
        

        for i in list(self.cases.keys()):
            case_num = i.split('case_')[1]
            level = int(case_num) + 2
            url = self.cases[i]['url']
            auth = self.cases[i]['auth']
            headers = self.cases[i]['headers']
            request_body = self.cases[i]['request_body']
            expected_start_code = str(self.cases[i]['expected_start_code'])
            test_case_passed = False




        
            if self.request_type == 'GET':
                response = requests.get(url, headers=headers, auth=auth)

            elif self.request_type == 'POST':
                response = requests.post(url, json=request_body, headers=headers, auth = auth)

            elif self.request_type == 'PUT':
                response = requests.put(url, json=request_body, headers=headers, auth = auth)

            elif self.request_type == 'DELETE':
                response = requests.delete(url, headers=headers, auth=auth)

            
        

            actual_response_code = response.status_code

            actual_response_body = ''
            try:
                actual_response_body = response.json()
            except:
                pass

            if str(actual_response_code).startswith(expected_start_code):
                test_case_passed = True



            workbook = openpyxl.load_workbook('TestCases.xlsx')

            sheet = workbook['Sheet']

            # Modify some cells



            sheet[f'{self.index_letter_dict[self.param_index_dict["actual_results__response_code"]]}{level}'] = str(actual_response_code)
            sheet[f'{self.index_letter_dict[self.param_index_dict["actual_results__response_body"]]}{level}'] = str(actual_response_body)
            sheet[f'{self.index_letter_dict[self.param_index_dict["test_passed"]]}{level}'] = str(test_case_passed)
            

            # Save the changes
            workbook.save('TestCases.xlsx')

            # Optionally, close the workbook
            workbook.close()


            





if __name__=='__main__':
    tester = Tester()
    if not tester.warning_present:
        tester.generate_excel()

        for i, v in list(tester.cases.items()):
            print('Case: '+ i)
            print('Data: ')
            print(v)


        approve_cases = tester.get_user_input('Do you approve the test cases above? 1 for yes, 0 for no\n', ['0', '1'])
        if approve_cases == '1':
            tester.test_cases()

        else:
            print('You have not approved the test cases')

