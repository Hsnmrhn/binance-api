# BINANCE ÜZERİNDEN COIN FIYATINI 5 DAKİKA ARALIKLARLA GUNCELLEYEN WEBAPP 

## 🚀 Kurulum Adımları

### 1️⃣ Gerekli Araçların Kurulumu
Aşağıdaki bileşenlerin sisteminizde yüklü olması gerekmektedir:
- **VirtualBox**
- **Multipass**

### 2️⃣ Multipass ile Ubuntu Instance Oluşturma

Apple Silicon tabanlı cihazlarda **ARM64** uyumlu bir Ubuntu instance başlatıyoruz:

```sh
multipass launch -n k8s-master --cpus 2 --mem 2G --disk 50G ubuntu@24.04
```

### 3️⃣ Kubernetes Cluster’ı Başlatma

Instance’a bağlanarak Kubernetes kurulumu yapıyoruz:

```sh
multipass shell k8s-master
```

### **Kubernetes Cluster Kurulumu**
#### **Ön Gereksinimler**
1. Tüm node'larda swap'i devre dışı bırakıyoruz:
```sh
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
```
2. Gerekli modülleri yüklüyoruz:
```sh
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter
```
3. Ağ ayarlarını yapılandırıyoruz:
```sh
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
sudo sysctl --system
```

### **Containerd Kurulumu**
1. Containerd'yi yüklüyoruz:
```sh
sudo apt-get update
sudo apt-get install -y containerd
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
# SystemdCgroup'u aktif ediyoruz. Yoksa workerları cluster’a ekleyemeyiz
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml
sudo systemctl restart containerd
```

### **Kubernetes Bileşenlerinin Kurulumu**
1. Kubernetes repository'sini ekliyoruz:
```sh
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
```
2. Kubernetes bileşenlerini yüklüyoruz:
```sh
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl 
```

### **Master Node Kurulumu**
1. Master node'u başlatıyoruz:
```sh
sudo kubeadm init --pod-network-cidr=192.168.0.0/16 --cri-socket # calico unix:///run/containerd/containerd.sock
```
2. Kubeconfig dosyasını ayarlıyoruz:
```sh
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

### 4️⃣ Control-Plane Üzerinde Pod Çalıştırmayı Etkinleştirme 
## ( Master Node Kurulumu Kısmını Atlayıp ***kubeadm token create --print-join-command*** dan elde ettiğmiz komutu worker node da sudo ile girerek master bağlıyor ve 1 master 1 worker nodedan oluşan cluster'ı kurmuş oluyoruz)

Varsayılan olarak, control-plane node’unda pod çalıştırılmasına izin verilmez. Bu kısıtlamayı kaldırıyoruz:

```sh
kubectl taint nodes $(kubectl get nodes -o jsonpath='{.items[0].metadata.name}') node-role.kubernetes.io/control-plane:NoSchedule-
kubectl taint nodes $(kubectl get nodes -o jsonpath='{.items[0].metadata.name}') node.kubernetes.io/not-ready:NoSchedule-
```

### 5️⃣ Ağ Eklentisi (CNI) Kurulumu

```sh
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
```

## 🛠️ Uygulama Dağıtımı

### 1️⃣ Docker İmajlarını Hazırlama

Uygulamamız iki bileşenden oluşmaktadır:
- **Backend**: Veriyi üretir ve bir **Persistent Volume (PV)** üzerine kaydeder.
- **Frontend**: PV üzerindeki veriyi okuyarak bir **web arayüzü** sunar.

Öncelikle Docker imajlarını oluşturalım:
### **Burada iki farklı mimari için iki farklı imaj oluşturuyoruz** 
```sh
docker build -t hsnmrhn/web .
docker build -t hsnmrhn/fetch-price .
```
```sh
docker build -t hsnmrhn/webapp .
docker build -t hsnmrhn/fetch .
```
Ardından, Docker Hub’a yükleyelim:
```sh
docker push hsnmrhn/web
docker push hsnmrhn/fetch-price
```
```sh
docker build -t hsnmrhn/webapp
docker build -t hsnmrhn/fetch
```

### 2️⃣ Kubernetes YAML Dosyalarını Uygulama

Kubernetes üzerine backend ve frontend’i dağıtıyoruz:

```sh
kubectl apply -f pv.yaml
kubectl apply -f pvc.yaml
kubectl apply -f webapp-deploy.yaml  # kubectl apply -f web-deploy.yaml --aarch işlemciler için
kubectl apply -f fetch-deployment.yaml # kubectl apply -f price-fetch-deploy.yaml --aarch işlemciler için
kubectl apply -f webapp-service.yaml
kubectl apply -f ingress.yaml
```

### 3️⃣ Ingress Controller Kurulumu

NGINX Ingress Controller’ı yükleyerek trafiği yönetiyoruz:

```sh
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```

### 4️⃣ Uygulamayı macOS Tarayıcısından Erişilebilir Hale Getirme
Multipass instance’ımızın IP adresini buluyoruz:
```sh
multipass list
```
Daha sonra macOS üzerinde `/etc/hosts` dosyasına aşağıdaki satırı ekleyelim:
```sh
echo "192.168.64.2 checkcurrency.case.local" | sudo tee -a /etc/hosts
```

Son olarak tarayıcıdan şu adresleri deneyelim:
- **http://192.168.64.2:30333**
- **http://checkcurrency.case.local:30333**





## 🏁 Sonuç
Bu adımları tamamladıktan sonra **Kubernetes üzerinde çalışan  uygulamamız oluyor!** 🚀


