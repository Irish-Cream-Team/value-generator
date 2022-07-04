
from random import choices
import click
import inquirer
import os

valuesDataBlock = """
name: {}
replicacounts: {}

images:
  PullSecrets: {}
  repository: {}
  tag: {}

configmap:
  configmaps: {}

service:
  ports:"""

serviceBlockData="""
    - name: {}
      port: {}
      tartgetPort: {} """

ingressBlockData = """
ingress:
  enabled: true
  hosts:
  - host: {}
    paths: """

ingressPathsBlockData = """
    - path: {}
      service: {}
      port: {}"""

helmFile = """
environments:
  dev:
  prod:

repositories:
- name: yesodot
  url: https://harborreg-2.northeurope.cloudapp.azure.com/chartrepo/library
  username: {{ requiredEnv "HARBOR_USER" }}
  password: {{ requiredEnv "HARBOR_PASSWORD" }}

releases:"""

releasesDataBlock = """
- name: {}
  namespace: {}
  chart: yesodot/common
  version: {{ requiredEnv "COMMON_VERSION" | default "0.5.2" }}
  values:
    - ../{{ .Environment.Name }}-values/{}.yaml
  installed: true """

releasename = []




def releasesCountFunc (namespace):
  for name in releasename:
    with open('helmfile.d/helm/helmfile.yaml', 'a') as yfile:
      yfile.write(releasesDataBlock.format(name,namespace,name))

def createHelmFile(namespace):
  with open('helmfile.d/helm/helmfile.yaml', 'w') as yfile:
      yfile.write(helmFile.format())    
  releasesCountFunc (namespace)

def valuesBlock(countsMicroservices,env): 
  for i in range(countsMicroservices):
    click.echo("enter data for the "+ str(countsMicroservices) + " microservice:")
    questions = [
    inquirer.Text("name", message="name " , default='default'),
    inquirer.Text("replicacount", message="number of replica " , default=1),
    inquirer.Text("repository", message="your image repository " , default='default'),
    inquirer.Text("pullSecrets", message="pullsecrets" , default='[]'),
    inquirer.Text("tag", message="image tag" , default='dev'),
    inquirer.Text("configMap", message="configMap" , default='[]'),
    ]
    answers = inquirer.prompt(questions)
    name = answers['name']
    replicacount = answers['replicacount']
    repository = answers['repository']
    pullSecrets = answers['pullSecrets']
    tag = answers['tag']
    configMap = answers['configMap']
    releasename.append(name)
    with open('helmfile.d/'+env+'-values/'+name+'.yaml', 'w') as yfile:
        yfile.write(valuesDataBlock.format(name,replicacount,repository,pullSecrets,tag,configMap))
    serviceBlock(name,env)

def serviceBlock(microServisName,env):
  questions = [
    inquirer.Text("serviceCount", message="enter how many service port you want?",default=1)]
  answers = inquirer.prompt(questions)
  serviceCount = answers['serviceCount']
  
  for i in range(int(serviceCount)):
    click.echo("enter data for the " + str(serviceCount) + " service port")
    questions = [
    inquirer.Text("name", message="port name" ,default="http"),
    inquirer.Text("port", message="port number " ,default=80),
    inquirer.Text("targetPort", message="target port number" ,default="80")]
    answers = inquirer.prompt(questions)
    name = answers['name']
    port = answers['port']
    targetPort = answers['targetPort']
    with open('helmfile.d/'+env+'-values/'+microServisName+'.yaml', 'a') as yfile:
      yfile.write(serviceBlockData.format(name, port,targetPort))
  questions = [
    inquirer.Text('createIngress', message="do you want ingress for your microservice (true/false)?",choices=['true', 'false'], default='false'),
    ]        
  answers = inquirer.prompt(questions)
  createIngress = answers['createIngress']
  if (createIngress == 'true'):
    ingressBlock(microServisName,env)
  
def ingressBlock(microServisName,env):
  click.echo("enter data for the ingress:")
  questions = [
    inquirer.Text("hostName", message="enter your host name ", default='default')]
  answers = inquirer.prompt(questions)
  hostName = answers['hostName']
  with open('helmfile.d/'+env+'-values/'+microServisName+'.yaml', 'a') as yfile:
    yfile.write(ingressBlockData.format(hostName))
  
  questions = [
    inquirer.Text("pathCount", message="enter how many paths you want", default=1)]
  answers = inquirer.prompt(questions)
  pathCount = answers['pathCount']
  for i in range(int(pathCount)):
    click.echo("enter data for the " + str(pathCount) + " path:")
    questions = [
    inquirer.Text("path", message="your path" ,default="/"),
    inquirer.Text("service", message="service name ", default='default'),
    inquirer.Text("port", message="port number" ,default="80")]
    answers = inquirer.prompt(questions)
    path = answers['path']
    service = answers['service']
    port = answers['port']
    with open('helmfile.d/'+env+'-values/'+microServisName+'.yaml', 'a') as yfile:
      yfile.write(ingressPathsBlockData.format(path,service,port))

@click.command()
@click.option('--countsmicroservices',default=1, prompt='how many microservices you want?')
@click.option('--namespace',default='abc', prompt='what is your namespace?')
@click.option('--env',default='dev', prompt='in which enviroment?')

def main(countsmicroservices,namespace,env):
  os.mkdir('helmfile.d')
  os.mkdir('helmfile.d/helm')
  os.mkdir('helmfile.d/dev-values')
  os.mkdir('helmfile.d/prod-values')
  valuesBlock(countsmicroservices,env)
  createHelmFile(namespace)
    # releasesCountFunc (imagename,countsMicroservices)

if __name__ == '__main__':
    main()
    ()
