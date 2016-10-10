import sys

__project__ = "django_json_api"
__version__ = "1.1.7"

from django.http import HttpResponse
import json, re, math

def xstr( s, none='' ):
  return str(s) if s is not None else none

def xint( s, none=0, undefined=None ):
  try:
    if s == "undefined":
      return undefined
    return int(s) if s is not None and s != 'NaN' else none
  except ValueError:
      #Floating points and trailing letters wont fool me!!!
    m = re.search('^[-+]?[0-9]+', s)
    if m:
      return int(m.group(0))

      #can't go any further
    return none
  except TypeError:
    return none

def xfloat( s, none=0.0, undefined=None ):
  try:
    if s == "undefined":
      return undefined
    f = float(s) if s is not None and s != 'NaN' else none
    if math.isnan(f):
      return none
    return f
  except ValueError:
      #trailing letters wont fool me!!!
    m = re.search('^[-+]?[0-9]*\.?[0-9]+', s )
    if m:
      return float(m.group(0))

      #Can't go any further
    return none
  except TypeError:
    return none

def xbool( s, none=False, undefined=False ):
    #Are we string? try to figure out what that means
  if isinstance( s, str ):
    s = s.lower()
    if s == 'true':
      return True
    elif s == 'none' or s == 'null':
      return none
    elif s == 'undefined':
      return undefined
    else:
      return False

    #Special case none
  elif s is None:
    return none
  else:
    return bool(s)

#value name converions
def _vn( n ):
  return ( n, None ) if (len(n) < 2 or n[1] != '#') else ( n[2:], n[0] )

#Value conversion
def _vc( t, r, v ):
  if t is None:
    return ( v, None )
  elif t == 'i':
    return ( xint(v), None )
  elif t == 'f':
    return ( xfloat(v), None )
  elif t == 'b':
    return ( xbool(v, none=None, undefined=None), None )
  elif t == 'j':
    try:
      return ( json.loads( v), None )
    except json.decoder.JSONDecodeError as e:
      return ( None, "Error processing json object %s [%s]" % (r, str(e)) )
  else:
    return ( v, None )

#Request args wrapper class
class reqArgs:
  def __init__(self, auth=None, get_args=[], post_args=[], get_opts=[], post_opts=[] ):
    def _arg( arg ):
      return [ arg ] if isinstance( arg, str ) else arg
    self.auth = auth
    self.get_args = _arg( get_args )
    self.post_args = _arg( post_args )
    self.get_opts = _arg( get_opts )
    self.post_opts = _arg( post_opts )

  def __call__(self, func):
    def wrapper( *args, **kwargs ):
        #Get my request object
      req_args = {}
      request = kwargs['request'] if 'request' in kwargs else args[0]
      get_missing = []
      post_missing = []


        #Internal function which runs the assignment action
      def pullArgs( request_args, req_dict, missing ):
        for x in request_args:
            #Get my key info
          contains = None
          if isinstance( x, tuple ) or isinstance( x, list ):
            n = x[0]
            contains = x[1]
          else:
            n = x
          r, t = _vn( n )

            #Don't allow args that already exist to be overwritten!
          if r in kwargs:
            req_args[r] = kwargs[r]
            continue
            #Get my item, if I don't have it, or there was an error, return None
          val = None
          if r in req_dict:
            val, err = _vc( t, r, req_dict[r] )
              #Did we get a parser error?
            if err is not None:
              return err

            #If json, check for contain keys, if the format is invalid, quit
          if t == 'j' and val is not None and contains is not None:
            if not all(k in val for k in contains):
              missing = []
              for k in contains:
                if k not in val:
                  missing.append( k )
              return "Invalid %s format. Required %s missing %s" % ( r, contains, missing)

            #Store the data
          if val is not None:
            kwargs[r] = req_args[r] = val
          elif missing is not None:
            missing.append( r )
          else:
            kwargs[r] = None

        return None

        #Required args
      err = pullArgs( self.post_args, request.POST, post_missing )
      if err is not None:
        return errResponse( request, err )
      err = pullArgs( self.get_args, request.GET, get_missing )
      if err is not None:
        return errResponse( request, err )

        #No missing accumulation
      err = pullArgs( self.post_opts, request.POST, None )
      if err is not None:
        return errResponse( request, err )
      err = pullArgs( self.get_opts, request.GET, None )
      if err is not None:
        return errResponse( request, err )

        #Are we good?
      if (len(get_missing) + len(post_missing)) > 0:
        return errResponse( request, 'Missing required argument(s): GET%s POST%s' % (str(get_missing), str(post_missing)))

        #Store all args into the requested args hash
      kwargs['req_args'] = req_args

        #Auth check?
      if self.auth is not None:
          #True for check authentication with default system auth
        if isinstance( self.auth, bool ):
          if self.auth:
            if not request.user.is_authenticated():
              return errResponse( request, "Not logged in")

          #Custom user authentication, we just just need a true/false
        elif hasattr( self.auth, '__call__'):
          if not self.auth( *args, **kwargs ):
            return errResponse( request, "Not logged in")

          #Not sure what we were pass, default to system authentication
        else:
          print("Unknown auth type, running default authentication to be safe")
          if not request.user.is_authenticated():
            return errResponse( request, "Not logged in")

      return func( *args, **kwargs)
    return wrapper

  #Json response
def jsonResponse( request, objs ):
  objs['successful'] = True
  callback = request.GET['callback'] if 'callback' in request.GET else None

  return rawResponse( json.dumps( objs ), status=200, content='application/json', callback=callback )

  #Return an error response
def errResponse( request, reason, extra={} ):
  print( reason )
  objs = { 'successful': False, 'reason': reason }
  objs.update( extra )
  callback = request.GET['callback'] if 'callback' in request.GET else None

  return rawResponse( json.dumps( objs ), status=201, content='application/json', callback=callback )

  #Raw response Info
def rawResponse( objs, status, content, callback=None ):
  if callback:
    return HttpResponse( "%s(%s)" % (callback, objs),
                         status=status, content_type=content )
  else:
    return HttpResponse( objs, status=status, content_type=content )
