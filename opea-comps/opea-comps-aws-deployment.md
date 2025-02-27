# OPEA GenAIComps Deployment Guide

This guide provides step-by-step instructions for deploying OPEA GenAIComps with TGI and Ollama on an AWS EC2 g4dn.xlarge instance with GPU support.

[OPEA GenAIComps Github](https://github.com/opea-project/GenAIComps.git)

[OPEA GenAI Microservices Documentation](https://opea-project.github.io/latest/microservices/index.html)

## 1. Launch AWS EC2 Instance

1. Launch a g4dn.xlarge instance with:
   - Ubuntu 22.04 LTS AMI
   - Root EBS volume of 40GB
   - Security group allowing ports 22, 8008, and 8009

## 2. Initial System Configuration

1. Connect to your instance:
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

2. Update the system:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. Configure NVMe instance storage:
   ```bash
   lsblk
   sudo mkfs.xfs /dev/nvme0n1
   sudo mkdir -p /mnt/docker-data
   sudo mount /dev/nvme0n1 /mnt/docker-data
   echo '/dev/nvme0n1 /mnt/docker-data xfs defaults,nofail 0 2' | sudo tee -a /etc/fstab
   ```

## 3. Install NVIDIA Drivers

1. Install NVIDIA drivers:
   ```bash
   sudo apt install -y linux-headers-$(uname -r)
   sudo apt install -y nvidia-driver-535 nvidia-utils-535
   ```

2. Reboot the instance:
   ```bash
   sudo reboot
   ```

3. Verify the GPU is detected:
   ```bash
   nvidia-smi
   ```

## 4. Install Docker and Docker Compose

1. Install Docker:
   ```bash
   sudo apt install -y docker.io
   ```

2. Configure Docker to use the instance storage:
   ```bash
   sudo mkdir -p /etc/docker
   sudo tee /etc/docker/daemon.json <<EOF
   {
     "data-root": "/mnt/docker-data"
   }
   EOF
   ```

3. Restart Docker:
   ```bash
   sudo systemctl restart docker
   ```

4. Add your user to the Docker group:
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

5. Install Docker Compose:
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

## 5. Install NVIDIA Container Toolkit

1. Add the NVIDIA Container Toolkit repository:
   ```bash
   curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
   
   sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null <<EOF
   deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://nvidia.github.io/libnvidia-container/stable/deb/ /
   EOF
   ```

2. Install the NVIDIA Container Toolkit:
   ```bash
   sudo apt update
   sudo apt install -y nvidia-container-toolkit
   ```

3. Configure Docker to use NVIDIA runtime:
   ```bash
   sudo tee /etc/docker/daemon.json <<EOF
   {
     "data-root": "/mnt/docker-data",
     "runtimes": {
       "nvidia": {
         "path": "nvidia-container-runtime",
         "runtimeArgs": []
       }
     }
   }
   EOF
   ```

4. Restart Docker:
   ```bash
   sudo systemctl restart docker
   ```

5. Test NVIDIA Docker:
   ```bash
   docker run --rm --gpus all nvidia/cuda:11.6.2-base-ubuntu20.04 nvidia-smi
   ```

## 6. Clone the OPEA GenAIComps Repository

1. Install Git:
   ```bash
   sudo apt install git -y
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/opea-project/GenAIComps.git
   cd GenAIComps/comps/third_parties
   ```

## 7. Configure Environment Variables

1. Get your external IP:
   ```bash
   external_ip=$(curl -s ifconfig.me)
   echo "Your external IP is: $external_ip"
   ```

2. Create the .env file:
   ```bash
   cat > .env << EOF
   host_ip=$external_ip
   LLM_ENDPOINT_PORT=8008
   MAX_INPUT_TOKENS=2048
   MAX_TOTAL_TOKENS=4096
   HF_TOKEN=
   EOF
   ```

3. Load the environment variables:
   ```bash
   export $(grep -v '^#' .env | xargs)
   ```

## 8. Configure Docker Compose for Both Services

1. Create the docker-compose.yml file:
   ```bash
   cat > docker-compose.yml << 'EOF'
   services:
     ollama-server:
       image: ollama/ollama
       container_name: ollama-server
       ports:
         - "8008:11434"
       volumes:
         - /mnt/docker-data/ollama:/root/.ollama
       environment:
         - host_ip=${host_ip}
       deploy:
         resources:
           reservations:
             devices:
               - driver: nvidia
                 count: all
                 capabilities: [gpu]
   
     tgi-server:
       image: ghcr.io/huggingface/text-generation-inference:latest
       container_name: tgi-server
       ports:
         - "8009:80"
       volumes:
         - /mnt/docker-data/tgi:/data
       environment:
         - MODEL_ID=google/flan-t5-small
         - NUM_SHARD=1
       deploy:
         resources:
           reservations:
             devices:
               - driver: nvidia
                 count: all
                 capabilities: [gpu]
   
   networks:
     default:
       driver: bridge
   EOF
   ```

2. Create model directories on the NVMe storage:
   ```bash
   sudo mkdir -p /mnt/docker-data/ollama
   sudo mkdir -p /mnt/docker-data/tgi
   sudo chown -R $USER:$USER /mnt/docker-data/ollama
   sudo chown -R $USER:$USER /mnt/docker-data/tgi
   ```

## 9. Start the Services

1. Start both services:
   ```bash
   docker-compose up -d
   ```

2. Verify that containers are running:
   ```bash
   docker ps
   ```

## 10. Pull Models and Test the Services

1. Pull a model with Ollama:
   ```bash
   curl -X POST http://localhost:8008/api/pull -d '{"model": "llama3"}'
   ```

2. Test Ollama with a simple query:
   ```bash
   curl -X POST http://localhost:8008/api/generate -d '{
     "model": "llama3",
     "prompt": "Please explain what machine learning is and give a few examples of its applications.",
     "stream": false
   }'
   ```

3. Test TGI:
   ```bash
   curl -X POST http://localhost:8009/generate \
     -H "Content-Type: application/json" \
     -d '{"inputs": "Answer this question: What is machine learning?", "parameters": {"max_new_tokens": 100}}'
   ```

## 11. Important Notes

1. **Data Persistence**: The NVMe instance storage is ephemeral and will be lost if the instance is stopped. For production use, consider setting up regular backups of important model files.

2. **Model Selection**: 
   - Ollama with llama3 provides better responses for most use cases
   - TGI with flan-t5-small works but gives shorter responses

3. **Resource Monitoring**: 
   ```bash
   # Monitor disk usage
   df -h
   
   # Monitor GPU usage
   nvidia-smi -l 1
   ```

4. **Service Management**:
   ```bash
   # Stop services
   docker-compose down
   
   # Start services
   docker-compose up -d
   
   # View logs
   docker logs ollama-server
   docker logs tgi-server
   ```

## 12. Troubleshooting

1. **Container Won't Start**: 
   - Check logs: `docker logs container_name`
   - Verify GPU access: `nvidia-smi`
   - Ensure Docker configuration is correct: `cat /etc/docker/daemon.json`

2. **Model Download Issues**:
   - Check network connectivity
   - For gated models, ensure valid HF_TOKEN is provided
   - Try smaller, open-access models first

3. **Docker Storage Problems**:
   - Verify mount: `df -h /mnt/docker-data`
   - Check Docker storage usage: `du -sh /mnt/docker-data/*`

4. **Port Connection Issues**:
   - Verify security group settings in AWS
   - Check service is running: `docker ps`
   - Test local access: `curl http://localhost:port/health`
