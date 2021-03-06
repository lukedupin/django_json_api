[![Build Status](https://travis-ci.org/lukedupin/django_json_api.svg?branch=master)](https://travis-ci.org/lukedupin/django_json_api)
[![PyPI](https://img.shields.io/pypi/v/django_json_api.svg?style=flat-square)](https://pypi.python.org/pypi/django_json_api/)
[![PyPI](https://img.shields.io/pypi/pyversions/django_json_api.svg?style=flat-square)](https://pypi.python.org/pypi/django_json_api/)


# Django Json API
Wrapper methods to streamline json based API communication through django.  This library is a simple set of calls which provide: 
* Variable injection
* Type conversion
* Json payload structure checking
* Json HTTP response
* Error response

# Installation

Assuming your django project has this basic structure for views, {{base}}/website/views.

	cd website/views
    git submodule add git@github.com:lukedupin/django_json_api.git json_api

# Usage

All @reqArgs arguments are optional, here is a list of them:

* get_args - Accepts a string, tuple, or array.  Key values specified here are ~required~ GET or URL variables.
* post_args - Accepts a string, tuple, or array.  Key values specified here are ~required~ POST variables.
* get_opts - Accepts a string, tuple, or array.  Key values specified here are ~optional~ GET or URL variables.
* post_opts - Accepts a string, tuple, or array.  Key values specified here are ~optional~ POST variables.
* auth - Accepts boolean True/False or a funciton call.  If Boolean true, default django authentication is used.  If a function, the funciton is called passing all arguments, and expects a boolean return (True authenticated, False not)

Build your url.py exactly the same way you would without @reqArgs.  @reqArgs operates entirely based on the JSON payload.  The variables loaded in with reqArgs wont overwrite possible variables from url.py.  Both play together nicely.

# Examples

Now inside your app, lets include the helper functions:

	from website.views.json_api import jsonResponse, errResponse, reqArgs
    
    	#Json wrapper
    @reqArgs( get_args=('i#project_id'),  #Required get arguments
              get_opts=('f#cats'),        #Optional get argument, converts to a float
              post_args=('action',       #Required post arguments
                         'i#permission'),
              post_opts=('i#user_id',    #Optional post arguments
                         'username',
                         'b#checked'))
    def api( request, project_id, action, permission, user_id, username, checked, **kwargs ):
        #project_id is already converted to an int, so we can just check it
        if project_id <= 0:
        	#Error always returns the structure { successful: False, reason: 'Error message' }
        	return errResponse( request, "Error message" )  #Errors just require a string, return json
            
        #No type qualifier means the variable is a string
        if action != "post":
            #Error with extra data
        	return errResponse( request, "Only accept posts", { 'data': {...}, 'details': "Awesome" })
            
        #Did we get a cats?
        if cats is not None:
        	return jsonResponse( request, { 'cat_type': 2.4 * cats } )
            
        #checked is a boolean, Here we generate a valid response
        if checked:
        	return jsonResponse( request, { 'message': "Nice work", 'data': {'type': 1 } )
 
 			#A valid json response, anything given inside the dict, will be returned as the json payload
            #Always returns { successful: True, message: 'great', data:{...} }
		return jsonResponse( request, { message: 'great', data: {...} })

Variable types can be specified.  The possible types are as folows:

* var - No conversion, variables will be strings.  IN ALL CASES the variable will be None if it doesn't exist.
* i#var - Convert value to an integer.  0 if no possible conversion.
* f#var - Convert value to a float.  0.0f if no possible conversion.
* b#var - Convert value to boolean.  False if none exists
* j#var - Convert value to dict using json.loads(content).  Error response if the conversion fails.  Also, if j# is used, an optional tuple can be passed, the second element of the tuple is a tuple of strings.  Each of these values will be checked against the resulting json object, ensuring all of those keys exist.  If a key is missing, a well formed error is returned to the user.  Example:  ('j#var', ('key1', 'key2', 'key3'))

Lets look at an example of json data inside our arguments:

	from website.views.json_api import jsonResponse, errResponse, reqArgs
    
    @reqArgs( get_args=('i#project_id'),  #Required get arguments
              post_args=('action',       #Required post arguments
                         'j#data'),
              post_opts=('i#user_id'))    #Optional post arguments
    def api( request, project_id, action, data, user_id, **kwargs ):
        #project_id is already converted to an int, so we can just check it
        if project_id <= 0:
        	return errResponse( request, "Error message" )  #Errors just require a string, return json
            
        a = data['key'] * 4
            
		return jsonResponse( request, {...})
        
    	#Notice this time, we ensure the json structure exists as we expect it to.
    contains = ('key1', 'key2')
    @reqArgs( get_args=('i#project_id'),
              post_opts=('j#data', contains))    #Now we ensure the keys in contains exist.  If they don't, an err response is sent before api is ever called.
    def api( request, project_id, data, **kwargs ):
        #project_id is already converted to an int, so we can just check it
        if project_id <= 0:
        	return errResponse( request, "Error message" )
            
       	#Now I know key1 and key2 exist
        if data is not None:
        	b = data['key1'] + data['key2']
            
		return jsonResponse( request, {...})
        
Perhaps we have optional arguments and we want to iterate through them?  No problem.  All key value pairs are captured inside the variable req_args.  req_args can be used in conjuction with function parameters:

    #Notice we don't have to have all the parameters listed in reqArgs
    #req_args will get all variables @reqArgs deals with
    @reqArgs( get_args=('i#project_id'),  #Required get arguments
    		  get_opts=('val', 'info', 'data', 'i#type'))
    def api( request, project_id, val, req_args, **kwargs ): 
        #project_id is already converted to an int, so we can just check it
        if project_id <= 0:
        	return errResponse( request, "Error message" )  #Errors just require a string, return json
            
           	#All variables the user passed are inside req_args
        info = {}
        for key in ('val', 'info', 'data', 'type'):
        	if key not in req_args:
            	continue
        	if key == 'val':
            	pass
            info[key] = req_args[key]
            
		return jsonResponse( request, {...})
        
Finally, lets say you want to call one of your methods that has @reqArgs?  No problem, but all variables need to be passed in as named variables, no positional variables are allowed:
 
	from website.views.json_api import jsonResponse, errResponse, reqArgs
    
    contains = ('key1', 'key2')
    @reqArgs( get_args=('i#project_id'),  #Required get arguments
              post_args=('action',       #Required post arguments
                         ('j#data', contains),
              post_opts=('i#user_id'))    #Optional post arguments
    def api( request, project_id, action, data, user_id, **kwargs ):
    	...
            
		return jsonResponse( request, {...})
 
    @reqArgs( get_args=('i#project_id'))  #Required get arguments
    def otherApi( request, project_id, **kwargs ):
    	#Do some different things
        
        #Call the reqArgs function, passing no positional arguments
		return api( request=request, project_id=project_id, action="update", data={})  #Notice its okay to leave out optional arguments
 
How about using the automatic user auth logic?

	from website.views.json_api import jsonResponse, errResponse, reqArgs
    
    @reqArgs( auth=True,					#Requires request.user.is_authenticated() to be true
    		  get_args=('i#project_id'))  	#Required get arguments
    def api( request, project_id, action, data, user_id, **kwargs ):
		return jsonResponse( request, {...})
 
 	def customAuth( request, project_id, **kwargs ):
    	if project_id == 4: #Authenticate the user that passes project_id == 4
        	return True
        else:
        	return request.user.id == 4 #If the logged in user's id is 4, success, else not authenticated
            
    @reqArgs( auth=customAuth,			  #Custom authenticate
    		  get_args=('i#project_id'))  #Required get arguments
    def otherApi( request, project_id, **kwargs ):
		return jsonResponse( request, {...})
        
# Common error

What if you run into this error?

    Internal Server Error: /user_info.json
    Traceback (most recent call last):
      File "/usr/lib/python3.5/site-packages/django/core/handlers/base.py", line 149, in get_response
        response = self.process_exception_by_middleware(e, request)
      File "/usr/lib/python3.5/site-packages/django/core/handlers/base.py", line 147, in get_response
        response = wrapped_callback(request, *callback_args, **callback_kwargs)
      File "xxx/website/views/json_api/__init__.py", line 188, in wrapper
        return func( *args, **kwargs)
    TypeError: userInfo() got an unexpected keyword argument 'req_args'
    
Good news, its easy to fix, you forgot to add **kwargs to the end of your function.  Convert your function from:

    @reqArgs( ... )
    def user_info( request, xxx):
    
To this:
    
    @reqArgs( ... )
    def user_info( request, xxx, **kwargs ):

Why does this happen?  Because a variable called ~req_args~ is always passed, the collection of all user specified variables.  Although you could specific ~req_args~ inside your function, in practice its better to always include **kwargs.
