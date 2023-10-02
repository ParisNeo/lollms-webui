from lollms.paths import gptqlora_repo
import subprocess
import gc
from lollms.helpers import ASCIIColors
from flask import jsonify, request


def start_training(self):
    if self.config.enable_gpu:
        if not self.lollms_paths.gptqlora_path.exists():
            # Clone the repository to the target path
            ASCIIColors.info("No gptqlora found in your personal space.\nCloning the gptqlora repo")
            subprocess.run(["git", "clone", gptqlora_repo, self.lollms_paths.gptqlora_path])
            subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=self.lollms_paths.gptqlora_path)
            
        data = request.get_json()
        ASCIIColors.info(f"--- Trainging of model {data['model_name']} requested ---")
        ASCIIColors.info(f"Cleaning memory:")
        fn = self.binding.binding_folder_name
        del self.binding
        self.binding = None
        self.model = None
        for per in self.mounted_personalities:
            per.model = None
        gc.collect()
        ASCIIColors.info(f"issuing command : python gptqlora.py --model_path {self.lollms_paths.personal_models_path/fn/data['model_name']}")
        subprocess.run(["python", "gptqlora.py", "--model_path", self.lollms_paths.personal_models_path/fn/data["model_name"]],cwd=self.lollms_paths.gptqlora_path)    
        return jsonify({'status':True})

def train(self):
    form_data = request.form

    # Create and populate the config file
    config = {
        'model_name': form_data['model_name'],
        'tokenizer_name': form_data['tokenizer_name'],
        'dataset_path': form_data['dataset_path'],
        'max_length': form_data['max_length'],
        'batch_size': form_data['batch_size'],
        'lr': form_data['lr'],
        'num_epochs': form_data['num_epochs'],
        'output_dir': form_data['output_dir'],
    }

    with open('train/configs/train/local_cfg.yaml', 'w') as f:
        yaml.dump(config, f)

    # Trigger the train.py script
    # Place your code here to run the train.py script with the created config file
    # accelerate launch --dynamo_backend=inductor --num_processes=8 --num_machines=1 --machine_rank=0 --deepspeed_multinode_launcher standard --mixed_precision=bf16  --use_deepspeed --deepspeed_config_file=configs/deepspeed/ds_config_gptj.json train.py --config configs/train/finetune_gptj.yaml

    subprocess.check_call(["accelerate","launch", "--dynamo_backend=inductor", "--num_processes=8", "--num_machines=1", "--machine_rank=0", "--deepspeed_multinode_launcher standard", "--mixed_precision=bf16", "--use_deepspeed", "--deepspeed_config_file=train/configs/deepspeed/ds_config_gptj.json", "train/train.py", "--config", "train/configs/train/local_cfg.yaml"])

    return jsonify({'message': 'Training started'})