import os
import re

import docker
import yaml


CORD_TAG = 'master'
GITHUB_BASE_URL = 'https://github.com'


def find_parent_names(dockerfile):
    with open(dockerfile, 'r') as f:
        lines = f.readlines()

    parent_names = []
    frompatt = re.compile(r'^FROM\s+([\w/_:.-]+)', re.MULTILINE)

    for line in lines:
        fromline = re.search(frompatt, line)
        if fromline:
            parent_names.append(fromline.group(1).split(':')[0])

    return parent_names


def fetch_repo(repo, tag):
    clone_command = '''
        mkdir -p ~/cord_repos \
        & git clone {base}/{repo}.git -b {tag} ~/cord_repos/{repo}
    '''.format(base=GITHUB_BASE_URL, repo=repo, tag=tag)
    os.system(clone_command)


def build_image(image_info, buildable=None, tag='latest'):
    image_name = image_info['name']
    print('Building %s...' % image_name)
    client = docker.DockerClient()
    fetch_repo(image_info['repo'], CORD_TAG)
    path = os.path.join(
        os.path.expanduser('~/cord_repos'),
        image_info['repo'],
        image_info.get('path', '.')
    )
    dockerfile = os.path.join(path, image_info.get('dockerfile', 'Dockerfile'))
    context_path = os.path.join(path, image_info.get('context', '.'))
    parents = find_parent_names(dockerfile)
    for parent in parents:
        if parent in (buildable or {}):
            build_image(buildable.pop(parent), buildable, tag)
    build_tag = '%s:%s' % (image_name, tag)

    for component in image_info.get('components', []):
        command = 'git clone {base}/{component}.git -b {tag} {path}'
        command = command.format(
            base=GITHUB_BASE_URL,
            component=component['repo'],
            path=os.path.join(context_path, component['dest']),
            repo=image_info['repo'],
            tag=CORD_TAG
        )
        os.system(command)

    client.images.build(
        path=context_path,
        dockerfile=dockerfile,
        tag=build_tag,
        rm=True,
        forcerm=True,
        pull=False
    )
    print('Done building %s.' % image_name)


if __name__ == "__main__":
    with open('docker_images.yml', 'r') as f:
        images = yaml.load(
            ' \n '.join(f.readlines())
        )

    buildable = {img['name']: img for img in images['buildable_images']}
    tag = images['docker_build_tag']

    while buildable:
        _, image_info = buildable.popitem()
        build_image(image_info, buildable, tag)
