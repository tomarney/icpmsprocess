import yaml

with open('settings.yml') as s:
  SETTINGS = yaml.safe_load(s)

with open('constants.yml') as c:
  CONST = yaml.safe_load(c)