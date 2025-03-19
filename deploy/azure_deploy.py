from azureml.core import Workspace, Model, Environment, InferenceConfig
from azureml.core.webservice import AciWebservice

ws = Workspace.from_config()

model = Model.register(workspace=ws, model_name="translator_model", model_path="backend/")

env = Environment("translation_env")
env.docker.enabled = True
env.python.conda_dependencies.add_pip_package("flask")
env.python.conda_dependencies.add_pip_package("pdfplumber")
env.python.conda_dependencies.add_pip_package("transformers")
env.python.conda_dependencies.add_pip_package("torch")
env.python.conda_dependencies.add_pip_package("sentence-transformers")

inference_config = InferenceConfig(entry_script="backend/translate_api.py", environment=env)

aci_config = AciWebservice.deploy_configuration(cpu_cores=2, memory_gb=4)

service = Model.deploy(ws, "translator-service", [model], inference_config, aci_config)
service.wait_for_deployment(show_output=True)
