from user_options import repo2
from setup.machine_inits import date

#
## Repositories to test, default is head of the trunk against personal repo.
## But if trunk is false, repo1 could be anything
#
trunk = True
repo1 = f"Trunk_{date}"
share_branch = False
repos = [repo1, repo2]
