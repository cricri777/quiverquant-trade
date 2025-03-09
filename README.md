# quiverquant-trade
monitoring insider trading

## Description
This project monitor quiverquant api for new congress trade, keep tracks of it and notify us

## Steps
1. read new input from quiverquant api
2. read history file
3. notify on not processed input
4. update history


## Prerequisites
Ensure you have the following installed:

- Python 3.10.11
- Packages: boto3, requests

## Installation for development
### Clone the repository:
```sh
git clone <your-repo-url>
cd quiverquant-trade
```

### Install the required packages:
```sh
pip install -r requirements.txt
```

## Deploy on AWS lambda
### Packaging
```shell
mkdir package
pip install -r requirements.txt -t package/
cp -r quiverquant_trade/* package/
cd package
zip -r ../lambda_function.zip .
cd ..
rm -rf package/
```

##### Upload Code


## Usage
1. Configure your JIRA and Tempo API settings in a configuration file inside `resources/config.yaml`
2. Run the main script to start the automation process:
```sh
python main.py
```

## License
This project is licensed under the MIT License—see the [LICENSE](LICENSE) file for details.