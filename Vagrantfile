# Vagrantfile for MRI Digital Twin

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y python3 python3-pip python3-venv git
    pip3 install poetry
  SHELL
end
