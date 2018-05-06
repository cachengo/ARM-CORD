To set up the system:
- Install docker
- Run: `pip install docker docker-compose`
- Run cord-bootstrap.sh
- Follow (WIKI)[https://guide.opencord.org/xos/dev/workflow_local.html] instructions for local configs
  - make PODCONFIG=rcord-local.yml config
  - make build

Note: Non-local configs depend on Vagrant which we don't have an ARM compatible way of installing yet.