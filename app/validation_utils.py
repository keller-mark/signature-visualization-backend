import re

def json_or(req, varname, default, validate=None):
  if req is None:
    return default
  else:
    try:
      val = req[varname]
      if not validate:
        return val
      else:
        regex = re.compile(validate)
        if isinstance(val, list):
          return list(filter(lambda x: regex.match(str(x)) != None, val))
        else:
          return val if regex.match(str(val)) else default
    except KeyError:
      return default