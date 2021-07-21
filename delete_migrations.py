import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

project_dir = "app"

project_name = "cryptocurrency"

apps = [
  "blockchain",
  "account"
]

for app in apps:
  current_path = f"{dir_path}/{project_dir}/{project_name}/{app}/migrations"
  for filename in os.listdir(f"{current_path}"):
    if filename != "__init__.py":
      os.system(f"rm -rf {current_path}/{filename}")