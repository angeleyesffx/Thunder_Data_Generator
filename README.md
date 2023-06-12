# Dynamic_Sender
**Install Python**

**IMPORTANT ---->>>>  This script needs Python 3.8 or above**

***Step 1:*** Download and Install the latest version of Python on the official site: https://www.python.org/downloads/
        
You can find Installation Guide to your system here:  https://realpython.com/installing-python/


***Step 2:*** Install or Update pip
        
You can find Installation Guide to your system here:  https://pypi.org/project/pip/

***Step 3:*** Create a virtual environment

Inside Script folder, follow the steps described at:

https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment

Then activate the virtual environment by running the command:

* `source env/bin/activate`

***Step 4:*** Install all dependencies listed on requirements.txt inside your project
        Execute the command line:
        
* `pip install -r requirements.txt` 

You can find information more information about command line here: https://docs.python.org/3/using/cmdline.html

You can find information more information about command line here: https://docs.python.org/3/using/cmdline.html

**IMPORTANT ---->>>> If you install python3 instead python using in command line python3:**


**How to execute the script through the terminal?** 

**IMPORTANT ---->>>>  If you're not sure that Dynamic Sender is building your requests correctly, check the information using Debug Mode. After corrected/verified run the application again, adding -e to your command line**


**Dynamic Sender has two distinct execution mode: Debug Mode and Execution Mode.**


**DEBUG MODE:**

Debug Mode is the default mode execution used to verify if the data is building correctly by Dynamic Sender, during Debug Mode execution no request will be sent through the application. 

 On terminal, you can run the command line changing the variables as you wish and removing the -e instruction: 


* `python3 main.py -CONFIG_YAML=(yaml_file_name) -FLOW=(execution_flow_name) -ENV= (environment) -COUNTRIES= (countries) -SERVICES= (services) -METHODS= (methods) -VERSIONS= (versions)` 


**EXECUTION MODE:**

Execution Mode is used to send requests through the application. To do an execution in this mode you need to add the instruction -e in the command line. 

This project was design to support some flexible parameters using environment variables. On terminal, you can run the command line changing the variables as you wish: 


* `python3 main.py -CONFIG_YAML=(yaml_file_name) -FLOW=(execution_flow_name) -ENV= (environment) -COUNTRIES= (countries) -SERVICES= (services) -METHODS= (methods) -VERSIONS= (versions) -e` 
 

If you want to change the default list of countries what Dynamic Sender will use in execution, to a specific list of countries, you can define it through the command line, using the environment variable “COUNTRIES”. Given the list, split by comma, the execution will proceed only by the countries that you defined.  

If you want to change the default list of entities what Dynamic Sender will use in execution, to a specific list of entities, you can define it through the command line, using the environment variable “ENTITIES”. Given the list, split by comma, the execution will proceed only by the entities that you defined.  

If you want to change the default list of methods what Dynamic Sender will use in execution, to a specific list of methods, you can define it through the command line, using the environment variable “METHODS”. Given the list, split by comma, the execution will proceed only by the methods that you defined. 

If you want to change the default list of versions what Dynamic Sender will use in execution, to a specific list of versions, you can define it through the command line, using the environment variable “VERSIONS”. Given the list, split by comma, the execution will proceed only by the versions that you defined. 

If you don’t know the order of flow you need, or you don’t know what microservices you need to call, you can choose one of the default flows that Thunder Data will use in execution. You can define it through the command line, using the environment variable “FLOW”.  

**For example:** 

If you want to execute the scenarios in the DEV environment only for Brazil and Argentina, on the Accounts entity, the methods POST, PUT,DELETE and versions V1 and V2 the command line that you need to run is:
* `python3 main.py -ENV=dev -COUNTRIES=br,ar -SERVICES=accounts -METHODS=post,put,delete   -VERSIONS=v1,v2 -e` 


If you decide to run a specific Yaml file:
* `python3 main.py -CONFIG_YAML= other_yaml -e` 


If you want to run a specific flow:
* `python3 main.py -FLOW= execution_flow_name -e` 

Or if you want to run everything using the default configuration:
* `python3 main.py -e`
 



