## Quick Guide ##
## Развертывание на сервере ##
1

    git clone https://github.com/smbd0x/CryptoFastAPI

2

    cd CryptoFastAPI

3

    docker-compose up --build

<b>По адресу <ip адрес или домен сервере>/docs можно посмотреть документацию и проверить работу API.</b>

Если на сервере уже установлен и запущен редис и он занимает нужный порт:

    sudo service redis-server stop

и повторно

    docker-compose up --build

## Если на сервере нет docker ##
<b>Можно попробовать установить через snap (для данного проекта все должно работать, но в целом при установке через snap в работе docker'а могут возникать ошибки):</b>

    sudo snap install docker

### Если со snap проблемы ###
<b>Обновление пакетов:<b>

    sudo apt update && sudo apt upgrade
    

<b>Команды для установки на Ubuntu из документации docker:<b>

1

    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
    
    # Add the repository to Apt sources:
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update

2

    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

3

    sudo docker run hello-world


