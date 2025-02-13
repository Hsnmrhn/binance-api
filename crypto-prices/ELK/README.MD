# ELK Stack Deployment Rehberi

Bu rehber, Kubernetes ortamında Elasticsearch, Logstash ve Kibana (ELK Stack) kurulumunu adım adım anlatmaktadır.

## 1. Helm ve Repo Ayarları
Öncelikle Helm yüklüyoruz.
```bash
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```

Ardından Elastic Helm repo'sunu ekleyin ve güncelliyoruz:

```bash
helm repo add elastic https://helm.elastic.co
helm repo update
```

## 2. Elasticsearch Deployment
Elasticsearch için özel ayarlarla bir `elasticsearch-values.yaml` dosyası oluşturuyoruz:

```yaml
# elasticsearch-values.yaml dosyası ELK klasörü altında
```

Daha sonra Elasticsearch'i helm ile deploy ediyoruz:

```bash
helm install elasticsearch elastic/elasticsearch -f elasticsearch-values.yaml
```

## 3. Logstash Deployment
Logstash için özel bir `logstash-values.yaml` dosyası oluşturuyoruz:

```yaml
# logstash-values.yaml
```

Logstash'i helm ile deploy ediyoruz:

```bash
helm install logstash elastic/logstash -f logstash-values.yaml
```

## 4. Kibana Deployment ve Harici Erişim
Kibana için `kibana-values.yaml` dosyasını oluşturuyoruz:

```yaml
# kibana-values.yaml
```

Kibana'yı helm ile deploy ediyoruz:

```bash
helm install kibana elastic/kibana -f kibana-values.yaml
```

## 5. Uygulama Log Konfigürasyonu
Uygulamanızı, Logstash'e log gönderecek şekilde yapılandırıyoruz. Örneğin, Java (Logback) için aşağıdaki gibi bir konfigürasyon kullanabilirsiniz:

```xml
<!-- logback.xml -->
<appender name="LOGSTASH" class="net.logstash.logback.appender.LogstashTcpSocketAppender">
  <destination>logstash-logstash:5000</destination>
  <encoder class="net.logstash.logback.encoder.LogstashEncoder"/>
</appender>
<root level="INFO">
  <appender-ref ref="LOGSTASH" />
</root>
```

## 6. DNS ve Erişim Testi
Kibana'ya erişebilmek için `/etc/hosts` dosyasına Ingress IP'sini ekliyoruz:

```bash
<INGRESS_IP> kibana.case.local
```

Tarayıcıdan `http://kibana.case.local` adresine giderek Kibana'ya erişimi test ediyoruz.

## 7. Logları Kontrol Etme
Kibana'ya girdikten sonra:
- "Stack Management > Index Patterns" kısmına gidip ve `app-logs-*` index pattern'ını oluşturuyoruz.
- "Discover" sekmesinden logları görüntülüyoruz.
