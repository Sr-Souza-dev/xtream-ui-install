#!/usr/bin/python3
# -*- coding: utf-8 -*-
import subprocess, os, random, string, sys, shutil, socket, zipfile, urllib.request, urllib.error
from itertools import cycle
from zipfile import ZipFile

# URLs para download dos arquivos principais e de sub-servidor (load balancer) do Xtream-UI.
rDownloadURL = {"main": "http://xtream-ui.org/main_xtreamcodes_reborn.tar.gz", "sub": "http://xtream-ui.org/sub_xtreamcodes_reborn.tar.gz"}
# Lista de pacotes que serão instalados no sistema.
rPackages = ["libcurl3", "libxslt1-dev", "libgeoip-dev", "e2fsprogs", "wget", "mcrypt", "nscd", "htop", "zip", "unzip", "mc", "libjemalloc1", "python3-paramiko", "mysql-server"] # Alterado python-paramiko para python3-paramiko
# Mapeamento para tipos de instalação (MAIN para servidor principal, LB para load balancer).
rInstall = {"MAIN": "main", "LB": "sub"}
# Mapeamento para o tipo de atualização.
rUpdate = {"UPDATE": "update"}
# Configuração do MySQL em formato base64, que será decodificada e gravada no arquivo my.cnf.
rMySQLCnf = "IyBYdHJlYW0gQ29kZXMKKFtjbGllbnRdCnBvcnQgICAgICAgICAgICA9IDMzMDYKCltteXNxbGRfc2FmZV0KbmljZSAgICAgICAgICAgID0gMAoKW215cWwxZgpkZWZhdWx0LWF1dGhlbnRpY2F0aW9uLXBsdWdpbj1teXNxbF9uYXRpdmVfcGFzc3dvcmQKdXNlciAgICAgICAgICAgID0gbXlxc2xKcG9ydCAgICAgICAgICAgID0gNzk5OQpiYXNlZGlyICAgICAgICAgID0gL3VzcmRhdGFkaXIgICAgICAgICA9IC92YXIvbGliL215c3FsdG1wZGlyICAgICAgICAgID0gL3RtcApjLW1lc3NhZ2VzLWRpciA9IC91c3Ivc2hhcmUvbXlxc2xza2lwLWV4dGVybmFsLWxvY2tpbmdza2lwLW5hbWUtcmVzb2x2ZT0xClvpbWQtYWRkcmVzcyAgICAgICAgICAgID0gKgpraWZfYnVmZmVyX3NpemUgPSAxMjhNbXlpc2FtX3NvcnRfYnVmZmVyX3NpemUgPSA0TQptYXhfYWxsb3dlZF9wYWNrZXQgICAgICA9IDY0TQpteWlzYW0tcmVjb3Zlci1vcHRpb25zID0gQkFDS1VQCm1heF9sZW5ndGhfZm9yX3NvcnRfZGF0YSA9IDgxOTIKcXVlcnlfY2FjaGVfbGltaXQgPSAwCnF1ZXJ5X2NhY2hlX3NpemUgPSAwCnF1ZXJ5X2NhY2hlX3R5cGUgPSAwCgpleHBpcmVfbG9nc19kYXlzID0gMTAKI2JpbmxvZ19leHBpcmVfbG9nc19zZWNvbmRzID0gODY0MDAwCm1heF9iaW5sb2dfc2l6ZSA9IDEwME0KdHJhbnNhY3Rpb25faXNvbGF0aW9uID0gUkVBRC1DT01NSVRURUQKbWF4X2Nvbm5lY3Rpb25zICA9IDEwMDAwCm9wZW5fZmlsZXNfbGltaXQgPSAxMDI0MAppbm5vZGJfb3Blbl9maWxlcyA9MTAyNDAKbWF4X2Nvbm5lY3RfZXJyb3JzID0gNDA5Ngp0YWJsZV9vcGVuX2NhY2hlID0gNDA5Ngp0YWJsZV9kZWZpbml0aW9uX2NhY2hlID0gNDA5Ngp0bXBfdGFibGVfc2l6ZSA9IDFHCm1heF9oZWFwX3RhYmxlX3NpemUgPSAxRwptYXhfZXhlY3V0aW9uX3RpbWUgPSAwCmJhY2tfbG9nID0gNDA5NgoKaW5ub2RiX2J1ZmZlcl9wb29sX3NpemUgPSA4Rwppbm5vZGJfYnVmZmVyX3Bvb2xfaW5zdGFuY2VzID0gOAppbm5vZGJfcmVhZF9pb190aHJlYWRzID0gNjQKaW5ub2RiX3dyaXRlX2lvX3RocmVhZHMgPSA2NAppbm5vZGJfdGhyZWFkX2NvbmN1cnJlbmN5ID0gMAppbm5vZGJfZnNfaF9sb2dfYXRfdHJ4X2NvbW1pdCA9IDAKaW5ub2RiX2ZsdXNoX21ldGhvZCA9IE9fRElSRUNUA3BlcmZvcm1hbmNlX3NjaGVtYSA9IDAKaW5ub2RiLWZpbGUtcGVyLXRhYmxlID0gMQppbm5vZGJfaW9fY2FwYWNpdHkgPSAxMDAwMAppbm5vZGJfdGFibGVfbG9ja3MgPSAwCmlubm9kYl9sb2NrX3dhaXRfdGltZW91dCA9IDAKaW5ub2RiX2RlYWRsb2NrX2RldGVjdCA9IDAKaW5ub2RiX2xvZ19maWxlX3NpemUgPSAxRwoKc3FsLW1vZGU9Ik5PX0VOR0lORV9TVUJTVElUVVRJT04iCgpbXG15c3FsZHVtcF0KcXVpY2sKcXVvdGUtbmFtZXMKbWF4X2FsbG93ZWRfcGFja2V0ICAgICAgPSAxMjhNQ29tcGxldGUtaW5zZXJ0CgpbX215c3FzXQoKW2lzYW1jaGtfZXZlcgprZXlfYnVmZmVyX3NpemUgICAgICAgICAgICAgID0gMTZN".encode("latin-1").decode("base64").decode("latin-1") # Adicionado .encode("latin-1").decode("base64").decode("latin-1")
# Configuração do arquivo de serviço do MySQL para systemd, também em base64.
rMySQLServiceFile = "IyBNeVNRTCBzeXN0ZW1kIHNlcnZpY2UgZmlsZQoKW1VuaXRdCkRlc2NyaXB0aW9uPU15U1FMIENvbW11bml0eSBTZXJ2aWNlCkFmdGVyPW5ldHdvcmsudGFyZ2V0CgpbSW5zdGFsbF0KV2FudGVkQnk9bXVsdGktdXNlci50YXJnZXQKC1tTZXJ2aWNlXQpUeXBlPWZvcmtpbmcKVXNlcj1teXNxbApHcm91cD1teXNxbApQSURGaWxlPS9ydW4vbXlzcWxkL215c3FsZC5waWQKVXBlcm1pc3Npb25zU3RhcnRPbmx5PXRydWUKRXhlY1N0YXJ0UHJlPS91c3Ivc2hhcmUvbXlzcWwvbXlzcWwtc3lzdGVtLXN0YXJ0IHByZ peelRVlY2VTdGFydD0vdXNyL3NiaW4vbXlzcWxkIC0tZGFlbW9uaXplIC0tcGlkLWZpbGU9L3J1bi9teXNxbGQvbXlzcWxkLnBpZCAuLi1tYXgtZXhlY3V0aW9uLXRpbWU9MApFbnZpcm9ubWVudEZpbGU9LS9ldGN2L215c3FsL215c2FsZApUaW1lb3V0U2VjPTYwMApSZXN0YXJ0PW9uLWZhaWx1cmUKUnVudGltZURpcmVjdG9yeT1teXNxbGRSdW50aW1lRGlyZWN0b3J5TW9kZT03NTVKb21pdE5PRklMRT01MDAw".encode("latin-1").decode("base64").decode("latin-1") # Adicionado .encode("latin-1").decode("base64").decode("latin-1")
# Configurações do sysctl em formato base64 para otimização de rede e kernel.
rSysCtl = "IyBmcm9tIFhVSS5vbmUgc2VydmVyCm5ldC5jb3JlLnNvbWF4Y29ubiA9IDY1NTM1MApuZXQuaXB2NC5yb3V0ZS5mbHVzaD0xCm5ldC5pcHY0LnRjcF9ub19tZXRyaWNzX3NhdmU9MQpuZXQuaXB2NC50Y3BfbW9kZXJhdGVfcmN2YnVmID0gMQpmcy5maWxlLW1heCA9IDY4MTU3NDQKZnMuYWlvLW1heC1uciA9IDY4MTU3NDQKZnMubnJfb3BlbiA9IDY4MTU3NDQKbmV0LmlwdjQuaXBfbG9jYWxfcG9ydF9yYW5nZSA9IDEwMjQgNjUwMDAKbmV0LmlwdjQudGNwX3NhY2sgPSAxCm5ldC5pcHY0LnRjcF9ybWVtID0gMTAwMDAwMDAgMTAwMDAwMDAgMTAwMDAwMDAKbmV0LmlwdjQudGNwX3dtZW0gPSAxMDAwMDAwMCAxMDAwMDAwMCAxMDAwMDAwMApuZXQuaXB2NC50Y3BfbWVtID0gMTAwMDAwMDAgMTAwMDAwMDAgMTAwMDAwMDAKbmV0LmNvcmUucm1lbV9tYXggPSA1MjQyODcKbmV0LmNvcmUud21lbV9tYXggPSA1MjQyODcKbmV0LmNvcmUucm1lbV9kZWZhdWx0ID0gNTI0Mjg3Cm5ldC5jb3JlLndtZW1fZGVmYXVsdCA9IDUyNDI4NwpuZXQuY29yZS5vcHRtZW1fbWF4ID0gNTI0Mjg3Cm5ldC5jb3JlLm5ldGRldl9tYXhfYmFja2xvZyA9IDMwMDAwMApuZXQuaXB2NC50Y3BfbWF4X3N5bl9iYWNrbG9nID0gMzAwMDAwCm5ldC5uZXRmaWx0ZXIubmZfY29ubnRyYWNrX21heD0xMjE1MTk2NjA4Cm5ldC5pcHY0LnRjcF93aW5kb3dfc2NhbGluZyA9ADEKdm0ubWF4X21hcF9jb3VudCA9IDY1NTMwMApuZXQuaXB2NC50Y3BfbWF4X3R3X2J1Y2tldHMgPSA1MDAwMApuZXQuaXB2Ni5jb25mLmFsbC5kaXNhYmxlX2lwdjYgPSAxCm5ldC5pcHY2LmNvbmYuZGVmYmVza3JpcHRpb24uZGlzYWJsZ_pcHJwdjYgPSAxCm5ldC5pcHY2LmNvbmYubG8uZGlzYWJsZV9pcHY2ID0gMQprZXJuZWwuc2htbWF4PTEzNDIxNzcyOAprZXJuZWwuc2htYWxsPTEzNDIxNzcyOAp2bS5vdmVyY29tbWl0X21lbW9yeSA9IDEKbmV0LmlwdjQudGNwX3R3X3JldXNlPTEKdm0uc3dhcHBpbmVzcz0xMA==".encode("latin-1").decode("base64").decode("latin-1") # Adicionado .encode("latin-1").decode("base64").decode("latin-1")
# Comentário indicando que as strings base64 são usadas para evitar problemas com caracteres de escape.

class col:
    # Esta classe define códigos de escape ANSI para colorir o texto no terminal.
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    YELLOW = '\033[33m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def generate(length=19):
    # Gera uma string aleatória de caracteres alfanuméricos com o comprimento especificado.
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

def getIP():
    # Obtém o endereço IP local do servidor.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80)) # Conecta a um servidor DNS público para obter o IP da interface de rede.
    return s.getsockname()[0]

def getVersion():
    # Retorna a versão do sistema operacional (distribuição Linux).
    try: return subprocess.check_output("lsb_release -d".split()).decode().split(":")[-1].strip() # Adicionado .decode() para lidar com a saída de bytes.
    except: return ""

def printc(rText, rColour=col.OKBLUE, rPadding=0):
    # Imprime uma mensagem centralizada em um "quadro" colorido no terminal.
    # rText: O texto a ser impresso.
    # rColour: A cor do texto e do quadro (padrão é azul).
    # rPadding: Número de linhas de preenchimento acima e abaixo do texto.
    print(f"{rColour} ┌──────────────────────────────────────────┐ {col.ENDC}") # Sintaxe de impressão atualizada com f-string.
    for i in range(rPadding): print(f"{rColour} │                                          │ {col.ENDC}") # Sintaxe de impressão atualizada com f-string.
    print(f"{rColour} │ {' '*(20-(len(rText)//2))}{rText}{' '*(40-(20-(len(rText)//2))-len(rText))} │ {col.ENDC}") # Sintaxe de impressão atualizada com f-string.
    for i in range(rPadding): print(f"{rColour} │                                          │ {col.ENDC}") # Sintaxe de impressão atualizada com f-string.
    print(f"{rColour} └──────────────────────────────────────────┘ {col.ENDC}") # Sintaxe de impressão atualizada com f-string.
    print(" ")

def prepare(rType="MAIN"):
    # Prepara o sistema para a instalação, removendo locks, atualizando pacotes e instalando dependências.
    # rType: Tipo de instalação ("MAIN" ou outro para load balancer).
    global rPackages
    if rType != "MAIN": rPackages = rPackages[:-3] # Se não for a instalação principal, remove os últimos 3 pacotes (provavelmente MySQL).
    printc("Preparing Installation")
    for rFile in ["/var/lib/dpkg/lock-frontend", "/var/cache/apt/archives/lock", "/var/lib/dpkg/lock"]:
        try: os.remove(rFile) # Tenta remover arquivos de lock do apt, caso existam.
        except: pass
    os.system("apt-get update > /dev/null") # Atualiza a lista de pacotes.
    printc("Removing libcurl4 if installed")
    os.system("apt-get remove --auto-remove libcurl4 -y > /dev/null") # Remove libcurl4, que pode causar conflitos.
    for rPackage in rPackages:
        printc(f"Installing {rPackage}") # Exibe o pacote que está sendo instalado.
        os.system(f"apt-get install {rPackage} -y > /dev/null") # Instala o pacote.
    printc("Installing libpng")
    os.system("wget -q -O /tmp/libpng12.deb http://mirrors.kernel.org/ubuntu/pool/main/libp/libpng/libpng12-0_1.2.54-1ubuntu1_amd64.deb") # Baixa o pacote libpng12.
    os.system("dpkg -i /tmp/libpng12.deb > /dev/null") # Instala o pacote libpng12.
    os.system("apt-get install -y > /dev/null") # Limpa dependências.
    try: os.remove("/tmp/libpng12.deb") # Remove o arquivo .deb baixado.
    except: pass
    try:
        subprocess.check_output("getent passwd xtreamcodes > /dev/null".split()) # Verifica se o usuário 'xtreamcodes' já existe.
    except:
        # Cria o usuário 'xtreamcodes' se ele não existir.
        printc("Creating user xtreamcodes")
        os.system("adduser --system --shell /bin/false --group --disabled-login xtreamcodes > /dev/null")
    if not os.path.exists("/home/xtreamcodes"): os.mkdir("/home/xtreamcodes") # Cria o diretório /home/xtreamcodes se não existir.
    return True

def install(rType="MAIN"):
    # Baixa e instala o software principal ou de load balancer.
    # rType: Tipo de instalação ("MAIN" ou "LB").
    global rInstall, rDownloadURL
    printc("Downloading Software")
    try: rURL = rDownloadURL[rInstall[rType]] # Obtém a URL de download com base no tipo de instalação.
    except KeyError: # Trata o erro se a URL não for encontrada.
        printc("Invalid download URL!", col.FAIL)
        return False
    os.system(f'wget -q -O "/tmp/xtreamcodes.tar.gz" "{rURL}"') # Baixa o arquivo compactado.
    if os.path.exists("/tmp/xtreamcodes.tar.gz"):
        printc("Installing Software")
        os.system('chattr -f -i /home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb > /dev/null') # Remove o atributo imutável do arquivo GeoLite2.mmdb.
        os.system('tar -zxvf "/tmp/xtreamcodes.tar.gz" -C "/home/xtreamcodes/" > /dev/null') # Extrai o arquivo para /home/xtreamcodes/.
        try: os.remove("/tmp/xtreamcodes.tar.gz") # Remove o arquivo compactado.
        except: pass
        return True
    printc("Failed to download installation file!", col.FAIL) # Mensagem de erro se o download falhar.
    return False

def update(rType="MAIN"):
    # Realiza a atualização do painel de administração ou instala o painel.
    # rType: Tipo de atualização ("UPDATE" para atualização manual, "MAIN" para instalação inicial do painel).
    if rType == "UPDATE":
        printc("Enter the link of release_xyz.zip file:", col.WARNING)
        rlink = input('Example: https://github.com/xtream-ui-org/xtream-ui-install/raw/master/files/release_22f.zip\n\nNow enter the link:\n\n') # Solicita o link do arquivo de atualização.
    else:
        rlink = "https://github.com/xtream-ui-org/xtream-ui-install/raw/master/files/release_22f.zip"
        printc("Installing Admin Panel")
    # Cabeçalhos HTTP para simular uma requisição de navegador.
    hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
    req = urllib.request.Request(rlink, headers=hdr) # Cria uma requisição HTTP.
    try:
        urllib.request.urlopen(req) # Tenta abrir a URL.
    except (urllib.error.URLError, urllib.error.HTTPError): # Captura erros de URL ou HTTP.
        printc("Invalid download URL!", col.FAIL)
        return False
    rURL = rlink
    printc("Downloading Software Update")  
    os.system(f'wget -q -O "/tmp/update.zip" "{rURL}"') # Baixa o arquivo de atualização.
    if os.path.exists("/tmp/update.zip"):
        try: is_ok = zipfile.ZipFile("/tmp/update.zip") # Tenta abrir o arquivo zip para verificar sua validade.
        except zipfile.BadZipFile: # Captura erro se o arquivo zip for inválido ou corrompido.
            printc("Invalid link or zip file is corrupted!", col.FAIL)
            os.remove("/tmp/update.zip")
            return False
        printc("Updating Software")
        # Série de comandos para descompactar a atualização, copiar arquivos e definir permissões.
        os.system('chattr -i /home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb > /dev/null && rm -rf /home/xtreamcodes/iptv_xtream_codes/admin > /dev/null && rm -rf /home/xtreamcodes/iptv_xtream_codes/pytools > /dev/null && unzip /tmp/update.zip -d /tmp/update/ > /dev/null && cp -rf /tmp/update/XtreamUI-master/* /home/xtreamcodes/iptv_xtream_codes/ > /dev/null && rm -rf /tmp/update/XtreamUI-master > /dev/null && rm -rf /tmp/update > /dev/null && wget -q https://github.com/xtream-ui-org/xtream-ui-install/raw/master/files/GeoLite2.mmdb -O /home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb > /dev/null && chown -R xtreamcodes:xtreamcodes /home/xtreamcodes/ > /dev/null && chmod +x /home/xtreamcodes/iptv_xtream_codes/permissions.sh > /dev/null && chattr +i /home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb > /dev/null')
        # Adiciona permissões específicas se não existirem no arquivo permissions.sh.
        if not "sudo chmod 400 /home/xtreamcodes/iptv_xtream_codes/config" in open("/home/xtreamcodes/iptv_xtream_codes/permissions.sh").read(): os.system('echo "#!/bin/bash\nsudo chmod -R 777 /home/xtreamcodes 2>/dev/null\nsudo find /home/xtreamcodes/iptv_xtream_codes/admin/ -type f -exec chmod 644 {} \; 2>/dev/null\nsudo find /home/xtreamcodes/iptv_xtream_codes/admin/ -type d -exec chmod 755 {} \; 2>/dev/null\nsudo find /home/xtreamcodes/iptv_xtream_codes/wwwdir/ -type f -exec chmod 644 {} \; 2>/dev/null\nsudo find /home/xtreamcodes/iptv_xtream_codes/wwwdir/ -type d -exec chmod 755 {} \; 2>/dev/null\nsudo chmod +x /home/xtreamcodes/iptv_xtream_codes/nginx/sbin/nginx 2>/dev/null\nsudo chmod +x /home/xtreamcodes/iptv_xtream_codes/nginx_rtmp/sbin/nginx_rtmp 2>/dev/null\nsudo chmod 400 /home/xtreamcodes/iptv_xtream_codes/config 2>/dev/null" > /home/xtreamcodes/iptv_xtream_codes/permissions.sh')
        # Substitui a URL do balancim.py para um espelho.
        os.system("sed -i 's|xtream-ui.com/install/balancer.py|github.com/emre1393/xtreamui_mirror/raw/master/balancer.py|g' /home/xtreamcodes/iptv_xtream_codes/pytools/balancer.py")
        os.system("sleep 2 && sudo /home/xtreamcodes/iptv_xtream_codes/permissions.sh > /dev/null") # Executa o script de permissões.
        try: os.remove("/tmp/update.zip") # Remove o arquivo de atualização.
        except: pass
        return True
    printc("Failed to download installation file!", col.FAIL) # Mensagem de erro se o download falhar.
    return False


def mysql(rUsername, rPassword):
    # Configura o servidor MySQL, criando o banco de dados e o usuário.
    # rUsername: Nome de usuário para o MySQL.
    # rPassword: Senha para o usuário MySQL.
    global rMySQLCnf
    printc("Configuring MySQL")
    rCreate = True
    if os.path.exists("/etc/mysql/my.cnf"):
        if open("/etc/mysql/my.cnf", "r").read(14) == "# Xtream Codes": rCreate = False # Verifica se o my.cnf já foi configurado pelo script.
    if rCreate:
        shutil.copy("/etc/mysql/my.cnf", "/etc/mysql/my.cnf.xc") # Faz backup do arquivo my.cnf existente.
        rFile = open("/etc/mysql/my.cnf", "w")
        rFile.write(rMySQLCnf) # Grava a nova configuração do MySQL.
        rFile.close()
        os.system("service mysql restart > /dev/null") # Reinicia o serviço MySQL.
    printc("Enter MySQL Root Password:", col.WARNING)
    for i in range(5): # Tenta 5 vezes a senha do root do MySQL.
        rMySQLRoot = input("  ") # Solicita a senha do root.
        print(" ") # Nova linha para formatação.
        if len(rMySQLRoot) > 0: rExtra = f" -p{rMySQLRoot}" # Adiciona a senha à string de comando se fornecida.
        else: rExtra = ""
        printc("Drop existing & create database? Y/N", col.WARNING)
        if input("  ").upper() == "Y": rDrop = True # Pergunta se deve dropar (excluir) o banco de dados existente.
        else: rDrop = False
        try:
            if rDrop:
                # Comandos MySQL para dropar o usuário e o banco de dados, criar o banco de dados, importar o schema, atualizar configurações e criar o novo usuário.
                os.system(f'mysql -u root{rExtra} -e "DROP USER IF EXISTS \'{rUsername}\'@\'%%\';" > /dev/null')
                os.system(f'mysql -u root{rExtra} -e "DROP DATABASE IF EXISTS xtream_iptvpro; CREATE DATABASE IF NOT EXISTS xtream_iptvpro;" > /dev/null')
                os.system(f"mysql -u root{rExtra} xtream_iptvpro < /home/xtreamcodes/iptv_xtream_codes/database.sql > /dev/null")
                os.system(f'mysql -u root{rExtra} -e "USE xtream_iptvpro; UPDATE settings SET live_streaming_pass = \'{generate(20)}\', unique_id = \'{generate(10)}\', crypt_load_balancing = \'{generate(20)}\', get_real_ip_client=\'\';" > /dev/null')
                os.system(f'mysql -u root{rExtra} -e "USE xtream_iptvpro; REPLACE INTO streaming_servers (id, server_name, domain_name, server_ip, vpn_ip, ssh_password, ssh_port, diff_time_main, http_broadcast_port, total_clients, system_os, network_interface, latency, status, enable_geoip, geoip_countries, last_check_ago, can_delete, server_hardware, total_services, persistent_connections, rtmp_port, geoip_type, isp_names, isp_type, enable_isp, boost_fpm, http_ports_add, network_guaranteed_speed, https_broadcast_port, https_ports_add, whitelist_ips, watchdog_data, timeshift_only) VALUES (1, \'Main Server\', \'\', \'{getIP()}\', \'\', NULL, NULL, 0, 25461, 1000, \'{getVersion()}\', \'eth0\', 0, 1, 0, \'\', 0, 0, \'{{}}\', 3, 0, 25462, \'low_priority\', \'\', \'low_priority\', 0, 1, \'\', 1000, 25463, \'\', \'[\"127.0.0.1\",\"\"]\', \'{{}}\', 0);" > /dev/null')
                os.system(f'mysql -u root{rExtra} -e "USE xtream_iptvpro; REPLACE INTO reg_users (id, username, password, email, member_group_id, verified, status) VALUES (1, \'admin\', \'\$6\$rounds=20000\$xtreamcodes\$XThC5OwfuS0YwS4ahiifzF14vkGbGsFF1w7ETL4sRRC5sOrAWCjWvQJDromZUQoQuwbAXAFdX3h3Cp3vqulpS0\', \'admin@website.com\', 1, 1, 1);" > /dev/null')
                os.system(f'mysql -u root{rExtra} -e "CREATE USER \'{rUsername}\'@\'%%\' IDENTIFIED BY \'{rPassword}\'; GRANT ALL PRIVILEGES ON xtream_iptvpro.* TO \'{rUsername}\'@\'%%\' WITH GRANT OPTION; GRANT SELECT, LOCK TABLES ON *.* TO \'{rUsername}\'@\'%%\';FLUSH PRIVILEGES;" > /dev/null')
                os.system(f'mysql -u root{rExtra} -e "USE xtream_iptvpro; CREATE TABLE IF NOT EXISTS dashboard_statistics (id int(11) NOT NULL AUTO_INCREMENT, type varchar(16) NOT NULL DEFAULT \'\', time int(16) NOT NULL DEFAULT \'0\', count int(16) NOT NULL DEFAULT \'0\', PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=latin1; INSERT INTO dashboard_statistics (type, time, count) VALUES(\'conns\', UNIX_TIMESTAMP(), 0),(\'users\', UNIX_TIMESTAMP(), 0);" > /dev/null')
                # A última linha é para prevenir uma vulnerabilidade XC, definindo get_real_ip_client como HTTP_CF_CONNECTING_IP se você estiver usando proxy CF.
                os.system(f'mysql -u root{rExtra} -e "USE xtream_iptvpro; UPDATE settings SET firewall=\'0\', flood_limit=\'0\', get_real_ip_client=\'\' where id=\'1\';" > /dev/null')
                if not os.path.exists("/etc/mysql/mysqld"): # Verifica se o arquivo mysqld existe.
                    if not "EnvironmentFile=-/etc/mysql/mysqld" in open("/lib/systemd/system/mysql.service").read(): 
                        os.system('echo "LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.1" > /etc/mysql/mysqld') # Adiciona pré-load da biblioteca jemalloc.
                        os.system(f'echo "{rMySQLServiceFile}" > /lib/systemd/system/mysql.service') # Grava o arquivo de serviço do MySQL.
                        os.system('systemctl daemon-reload; systemctl restart mysql.service;') # Recarrega e reinicia o serviço MySQL.
            try: os.remove("/home/xtreamcodes/iptv_xtream_codes/database.sql") # Remove o arquivo de schema do banco de dados.
            except: pass
            return True
        except Exception as e: printc(f"Invalid password! Try again ({e})", col.FAIL) # Mensagem de erro para senha inválida do MySQL root.
    return False

def encrypt(rHost="127.0.0.1", rUsername="user_iptvpro", rPassword="", rDatabase="xtream_iptvpro", rServerID=1, rPort=7999):
    # Criptografa as informações de conexão do banco de dados e as salva no arquivo de configuração.
    # rHost: Endereço do host do MySQL.
    # rUsername: Nome de usuário do MySQL.
    # rPassword: Senha do MySQL.
    # rDatabase: Nome do banco de dados MySQL.
    # rServerID: ID do servidor.
    # rPort: Porta do MySQL.
    printc("Encrypting...")
    try: os.remove("/home/xtreamcodes/iptv_xtream_codes/config") # Remove o arquivo de configuração existente.
    except: pass
    rf = open('/home/xtreamcodes/iptv_xtream_codes/config', 'wb') # Abre o arquivo de configuração em modo de escrita binária.
    # Codifica a string de dados de conexão em bytes, aplica uma XOR cíclica com uma chave e depois converte para hexadecimal.
    data_to_encrypt = '{"host":"%s","db_user":"%s","db_pass":"%s","db_name":"%s","server_id":"%d", "db_port":"%d"}' % (rHost, rUsername, rPassword, rDatabase, rServerID, rPort)
    encrypted_data = b''.join(bytes([ord(c)^ord(k)]) for c,k in zip(data_to_encrypt, cycle('5709650b0d7806074842c6de575025b1'))).hex()
    rf.write(encrypted_data.encode('ascii')) # Escreve os dados criptografados no arquivo.
    rf.close()

def configure():
    # Configura várias partes do sistema, como fstab, sudoers, scripts de inicialização, e otimizações.
    printc("Configuring System")
    if not "/home/xtreamcodes/iptv_xtream_codes/" in open("/etc/fstab").read(): # Verifica se as entradas do fstab já existem.
        rFile = open("/etc/fstab", "a")
        # Adiciona entradas ao fstab para montar diretórios como tmpfs (RAM disk).
        rFile.write("tmpfs /home/xtreamcodes/iptv_xtream_codes/streams tmpfs defaults,noatime,nosuid,nodev,noexec,mode=1777,size=90% 0 0\ntmpfs /home/xtreamcodes/iptv_xtream_codes/tmp tmpfs defaults,noatime,nosuid,nodev,noexec,mode=1777,size=2G 0 0")
        rFile.close()
    if not "xtreamcodes" in open("/etc/sudoers").read(): # Verifica se a entrada do sudoers para xtreamcodes existe.
        os.system('echo "xtreamcodes ALL = (root) NOPASSWD: /sbin/iptables, /usr/bin/chattr" >> /etc/sudoers') # Adiciona permissões sudo para o usuário xtreamcodes.
    if not os.path.exists("/etc/init.d/xtreamcodes"): # Verifica se o script de inicialização existe.
        rFile = open("/etc/init.d/xtreamcodes", "w")
        rFile.write("#! /bin/bash\n/home/xtreamcodes/iptv_xtream_codes/start_services.sh") # Cria o script de inicialização.
        rFile.close()
        os.system("chmod +x /etc/init.d/xtreamcodes > /dev/null") # Define permissões de execução.
    try: os.remove("/usr/bin/ffmpeg") # Remove o link simbólico existente para ffmpeg.
    except: pass
    if rType == "MAIN": 
        # Edita esses 2 arquivos para retornar a resposta da API sem o IP do servidor principal, o que é útil se você usar um proxy na frente do seu servidor principal.
        os.system("mv /home/xtreamcodes/iptv_xtream_codes/wwwdir/panel_api.php /home/xtreamcodes/iptv_xtream_codes/wwwdir/.panel_api_original.php && wget -q https://github.com/xtream-ui-org/xtream-ui-install/raw/master/files/panel_api.php -O /home/xtreamcodes/iptv_xtream_codes/wwwdir/panel_api.php")
        os.system("mv /home/xtreamcodes/iptv_xtream_codes/wwwdir/player_api.php /home/xtreamcodes/iptv_xtream_codes/wwwdir/.player_api_original.php && wget -q https://github.com/xtream-ui-org/xtream-ui-install/raw/master/files/player_api.php -O /home/xtreamcodes/iptv_xtream_codes/wwwdir/player_api.php")
    if not os.path.exists("/home/xtreamcodes/iptv_xtream_codes/tv_archive"): os.mkdir("/home/xtreamcodes/iptv_xtream_codes/tv_archive/") # Cria o diretório de arquivo de TV.
    os.system("ln -s /home/xtreamcodes/iptv_xtream_codes/bin/ffmpeg /usr/bin/") # Cria um link simbólico para o ffmpeg.
    os.system("wget -q https://github.com/xtream-ui-org/xtream-ui-install/raw/master/files/GeoLite2.mmdb -O /home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb") # Baixa o banco de dados GeoLite2.
    os.system("wget -q https://github.com/xtream-ui-org/xtream-ui-install/raw/master/files/pid_monitor.php -O /home/xtreamcodes/iptv_xtream_codes/crons/pid_monitor.php") # Baixa o script de monitoramento de PID.
    os.system("chown xtreamcodes:xtreamcodes -R /home/xtreamcodes > /dev/null") # Altera o proprietário dos arquivos.
    os.system("chmod -R 0777 /home/xtreamcodes > /dev/null") # Define permissões amplas (777).
    os.system("chattr +i /home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb > /dev/null") # Define o atributo imutável para GeoLite2.mmdb.
    os.system("sed -i 's|chown -R xtreamcodes:xtreamcodes /home/xtreamcodes|chown -R xtreamcodes:xtreamcodes /home/xtreamcodes 2>/dev/null|g' /home/xtreamcodes/iptv_xtream_codes/start_services.sh") # Modifica o start_services.sh para ignorar erros de chown.
    os.system("chmod +x /home/xtreamcodes/iptv_xtream_codes/start_services.sh > /dev/null") # Define permissões de execução para start_services.sh.
    os.system("mount -a") # Monta todos os sistemas de arquivos listados em fstab.
    os.system("chmod 0700 /home/xtreamcodes/iptv_xtream_codes/config > /dev/null") # Define permissões restritivas para o arquivo de configuração.
    os.system("sed -i 's|echo \"Xtream Codes Reborn\";|header(\"Location: https://www.google.com/\");|g' /home/xtreamcodes/iptv_xtream_codes/wwwdir/index.php") # Redireciona a página inicial.
    # Novas configurações sysctl.conf
    os.system("/bin/cp /etc/sysctl.conf /etc/sysctl.conf.bak") # Faz backup do sysctl.conf.
    os.system(f'echo "{rSysCtl}" > /etc/sysctl.conf') # Grava as novas configurações do sysctl.
    os.system("/sbin/sysctl -p > /dev/null") # Carrega as novas configurações do sysctl.
    # Novos aliases, atalhos, restartpanel e reloadnginx
    os.system('echo "alias restartpanel=\'sudo /home/xtreamcodes/iptv_xtream_codes/start_services.sh && echo done\'\nalias reloadnginx=\'sudo /home/xtreamcodes/iptv_xtream_codes/nginx/sbin/nginx -s reload && echo done\'" > /root/.bash_aliases') # Adiciona aliases ao bash.
    os.system("source /root/.bashrc > /dev/null") # Recarrega o .bashrc para ativar os aliases.
    if not "api.xtream-codes.com" in open("/etc/hosts").read(): os.system('echo "127.0.0.1    api.xtream-codes.com" >> /etc/hosts') # Bloqueia domínios antigos no /etc/hosts.
    if not "downloads.xtream-codes.com" in open("/etc/hosts").read(): os.system('echo "127.0.0.1    downloads.xtream-codes.com" >> /etc/hosts')
    if not "xtream-codes.com" in open("/etc/hosts").read(): os.system('echo "127.0.0.1    xtream-codes.com" >> /etc/hosts')
    if not "@reboot root /home/xtreamcodes/iptv_xtream_codes/start_services.sh" in open("/etc/crontab").read(): os.system('echo "@reboot root /home/xtreamcodes/iptv_xtream_codes/start_services.sh" >> /etc/crontab') # Adiciona entrada no crontab para iniciar os serviços no boot.

def start(first=True):
    # Inicia ou reinicia os serviços do Xtream Codes.
    # first: Booleano indicando se é a primeira inicialização.
    if first: printc("Starting Xtream Codes")
    else: printc("Restarting Xtream Codes")
    os.system("/home/xtreamcodes/iptv_xtream_codes/start_services.sh > /dev/null") # Executa o script de início dos serviços.

def modifyNginx():
    # Modifica a configuração do Nginx para adicionar um novo bloco de servidor.
    printc("Modifying Nginx")
    rPath = "/home/xtreamcodes/iptv_xtream_codes/nginx/conf/nginx.conf"
    rPrevData = open(rPath, "r").read()
    if not "listen 25500;" in rPrevData: # Verifica se a porta 25500 já está configurada.
        shutil.copy(rPath, f"{rPath}.xc") # Faz backup do arquivo nginx.conf.
        # Adiciona um novo bloco de servidor ao nginx.conf.
        rData = "}".join(rPrevData.split("}")[:-1]) + "    server {\n        listen 25500;\n        index index.php index.html index.htm;\n        root /home/xtreamcodes/iptv_xtream_codes/admin/;\n\n        location ~ \.php$ {\n            limit_req zone=one burst=8;\n            try_files $uri =404;\n         fastcgi_index index.php;\n          fastcgi_pass php;\n         include fastcgi_params;\n           fastcgi_buffering on;\n         fastcgi_buffers 96 32k;\n           fastcgi_buffer_size 32k;\n          fastcgi_max_temp_file_size 0;\n         fastcgi_keep_conn on;\n         fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;\n         fastcgi_param SCRIPT_NAME $fastcgi_script_name;\n        }\n    }\n}"
        rFile = open(rPath, "w")
        rFile.write(rData) # Grava a nova configuração.
        rFile.close()

if __name__ == "__main__":
    # Bloco principal de execução do script.
    rType = input("  Installation Type [MAIN, LB, UPDATE]: ") # Solicita o tipo de instalação.
    if rType.upper() in ["MAIN", "LB"]:
        if rType.upper() == "LB":
            rHost = input("  Main Server IP Address: ") # Solicita o IP do servidor principal para load balancer.
            try: rServerID = int(input("  Load Balancer Server ID: ")) # Solicita o ID do servidor do load balancer.
            except ValueError: rServerID = -1 # Trata erro se o ID não for um número.
            print(" ")
        else:
            rHost = "127.0.0.1" # IP padrão para instalação principal.
            rServerID = 1 # ID padrão do servidor.
            
        rPassword = input("  MySQL Password: ") # Solicita a senha do MySQL.
        rUsername = "user_iptvpro" # Nome de usuário padrão do MySQL.
        rDatabase = "xtream_iptvpro" # Nome do banco de dados padrão.
        rPort = 7999 # Porta padrão do MySQL.

        if len(rHost) > 0 and len(rPassword) > 0 and rServerID > -1: # Valida as entradas.
            printc("Start installation? Y/N", col.WARNING)
            if input("  ").upper() == "Y": # Confirmação para iniciar a instalação.
                print(" ")
                rRet = prepare(rType.upper()) # Prepara o sistema.
                if not install(rType.upper()): sys.exit(1) # Instala o software.
                if rType.upper() == "MAIN":
                    if not mysql(rUsername, rPassword): sys.exit(1) # Configura o MySQL se for a instalação principal.
                encrypt(rHost, rUsername, rPassword, rDatabase, rServerID, rPort) # Criptografa as credenciais do DB.
                configure() # Configura o sistema.
                if rType.upper() == "MAIN": 
                    modifyNginx() # Modifica o Nginx.
                    update(rType.upper()) # Atualiza o painel de administração.
                start() # Inicia os serviços.
                printc("Installation completed!", col.OKGREEN, 2) # Mensagem de sucesso.
                if rType.upper() == "MAIN":
                    printc("Please store your MySQL password!") # Lembra de armazenar a senha do MySQL.
                    printc(rPassword) # Exibe a senha gerada.
                    printc(f"Admin UI: http://{getIP()}:25500") # Exibe o URL da interface de administração.
                    printc("Admin UI default login is admin/admin") # Informa o login padrão.
            else: printc("Installation cancelled", col.FAIL) # Mensagem de cancelamento.
        else: printc("Invalid entries", col.FAIL) # Mensagem de entradas inválidas.
    elif rType.upper() == "UPDATE":
        if os.path.exists("/home/xtreamcodes/iptv_xtream_codes/wwwdir/api.php"): # Verifica se o painel principal está instalado.
            printc("Update Admin Panel? Y/N?", col.WARNING)
            if input("  ").upper() == "Y": # Confirmação para atualizar o painel.
                if not update(rType.upper()): sys.exit(1) # Executa a atualização.
                printc("Installation completed!", col.OKGREEN, 2) # Mensagem de sucesso.
                start() # Inicia os serviços.
            else: printc("Install Xtream Codes Main first!", col.FAIL) # Mensagem de erro se o painel não estiver instalado.
        else: printc("Install Xtream Codes Main first!", col.FAIL) # Adicionado este bloco else para clareza.
    else: printc("Invalid installation type", col.FAIL) # Mensagem para tipo de instalação inválido.