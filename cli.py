
# from random import choices
import click
import inquirer
import os
import re

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

def validate_number(answers, value):
  try:
    if int(value) <= 0:
      raise ValueError(value)
    else:
      return value
  except ValueError:
    click.echo('\n given invalide number,should be larger than zero')

def validate_bool(answers, value):
  try:
    if value != 'false' and value != 'true':
      raise ValueError(value)
    else:
      return value
  except ValueError:
    click.echo('\n given invalide value,should be false or true')

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
    click.echo("Please enter data for microservice #"+ str(countsMicroservices))
    questions = [
    inquirer.Text("name", message="name " , default='default'),
    inquirer.Text("replicacount", message="number of replica " , validate=validate_number),
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
    inquirer.Text("serviceCount", message="number of ports",validate=validate_number)]
  answers = inquirer.prompt(questions)
  serviceCount = answers['serviceCount']
  
  for i in range(int(serviceCount)):
    click.echo("Please enter data for service port  #" + str(serviceCount))
    questions = [
    inquirer.Text("name", message="port name" ,default="http"),
    inquirer.Text("port", message="port number" ,validate=validate_number),
    inquirer.Text("targetPort", message="target port number" ,validate=validate_number)]
    answers = inquirer.prompt(questions)
    name = answers['name']
    port = answers['port']
    targetPort = answers['targetPort']
    with open('helmfile.d/'+env+'-values/'+microServisName+'.yaml', 'a') as yfile:
      yfile.write(serviceBlockData.format(name, port,targetPort))
  questions = [
    inquirer.Text('createIngress', message="Create ingress? (true/false)?", validate=validate_bool)
    ]        
  answers = inquirer.prompt(questions)
  createIngress = answers['createIngress']
  if (createIngress == 'true'):
    ingressBlock(microServisName,env)
  
def ingressBlock(microServisName,env):
  click.echo("Please data for ingress:")
  questions = [
    inquirer.Text("hostName", message="host name", default='default')]
  answers = inquirer.prompt(questions)
  hostName = answers['hostName']
  with open('helmfile.d/'+env+'-values/'+microServisName+'.yaml', 'a') as yfile:
    yfile.write(ingressBlockData.format(hostName))
  
  questions = [
    inquirer.Text("pathCount", message="number of paths: ", validate=validate_number)]
  answers = inquirer.prompt(questions)
  pathCount = answers['pathCount']
  for i in range(int(pathCount)):
    click.echo("Please enter data for path  #" + str(pathCount))
    questions = [
    inquirer.Text("path", message="your path" ,default="/"),
    inquirer.Text("service", message="service name", default='default'),
    inquirer.Text("port", message="port number" ,validate=validate_number)]
    answers = inquirer.prompt(questions)
    path = answers['path']
    service = answers['service']
    port = answers['port']
    with open('helmfile.d/'+env+'-values/'+microServisName+'.yaml', 'a') as yfile:
      yfile.write(ingressPathsBlockData.format(path,service,port))

def val(ctx, param, value):
  try:
    if int(value) <= 0:
      raise ValueError(value)
    else:
      return value
  except ValueError:
    click.echo('Invalide number microservices given,should be larger than zero')
    value = click.prompt(param.prompt)
    return val(ctx, param, value)
    

@click.command()
@click.option('--countsmicroservices',type=click.INT, prompt='number of microservices',required=True,callback=val)
@click.option('--namespace',default='abc', prompt='namespace')
@click.option('--env',default='dev', prompt='enviroment')

def main(countsmicroservices,namespace,env):
  if os.path.isdir('helmfile.d'):
    click.echo("The helmfile folder already exists")
  else:
    os.mkdir('helmfile.d')
    os.mkdir('helmfile.d/helm')
    os.mkdir('helmfile.d/dev-values')
    os.mkdir('helmfile.d/prod-values')
    valuesBlock(countsmicroservices,env)
    createHelmFile(namespace)
  

if __name__ == '__main__':
    main()
    ()
