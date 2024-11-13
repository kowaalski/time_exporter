# Timezone Local Hour Exporter

This Python script exports the local hour and UTC offset for all available timezones as metrics that can be scraped by Prometheus. The script automatically adjusts for daylight saving time (DST) across different regions.

## Features

- Exports the local hour for all timezones globally.
- Exports the current UTC offset for each timezone.
- Automatically adjusts for daylight saving time (summer/winter).
- Exposes metrics via an HTTP server for Prometheus to scrape.
- Uses Prometheus metrics with labels to identify different timezones and their respective UTC offsets.

## How It Works

The script uses the `prometheus_client` library to define and expose `Gauge` metrics with labels. It calculates the current hour and UTC offset for each timezone available in the `pytz` library and updates the corresponding Prometheus metrics every 60 seconds.

### Key Components

- **`CollectorRegistry`**:
  - A `CollectorRegistry` is an object provided by the `prometheus_client` library that acts as a container for your metrics. It is where you register the metrics that you want to expose to Prometheus.
  - By default, Prometheus uses a global `CollectorRegistry` that automatically includes some default metrics, such as Python runtime information and garbage collection statistics. However, in this script, we create a custom `CollectorRegistry` to have full control over which metrics are exposed. This avoids exposing unnecessary metrics and keeps our Prometheus endpoint clean and focused.
  - In the script, we create the `CollectorRegistry` like this:

    ```python
    registry = CollectorRegistry(auto_describe=False)
    ```

    - `auto_describe=False`: This parameter is used to disable the automatic description of metrics. This can be useful to optimize performance and avoid automatically generated descriptions for metrics that may not need them.

- **`get_local_hour_and_offset(timezones)`**:
  - This function takes a list of timezone strings and returns a dictionary where the keys are timezone names and the values are tuples containing the local hour, formatted UTC offset string, and the numeric UTC offset in hours.
  - It handles the conversion from UTC to the specified timezone and adjusts automatically for daylight saving time.

- **Prometheus `Gauge` Metrics with Labels**:
  - **Local Hour Metric**: A `Gauge` metric named `local_hour` is used to track the current local hour in each timezone. This metric has a `timezone` label to differentiate the local hours across different timezones.
  - **UTC Offset Metric**: Another `Gauge` metric named `timezone_utc_offset` is used to track the current UTC offset for each timezone. This metric has two labels: `timezone` and `utc_offset`. The value of this metric represents the UTC offset in hours, which can be positive or negative.

### Example Usage

The script defines two `Gauge` metrics:
- **`local_hour`**: Tracks the current local hour for each timezone.
- **`timezone_utc_offset`**: Tracks the current UTC offset in hours for each timezone.

These metrics are updated every minute and can be scraped by Prometheus.

### Example Output

Once the script is running, you can visit `http://localhost:8000/metrics` to view the metrics. You should see something like:

```plaintext
# HELP local_hour Current local hour in the specified timezone, automatically adjusted for daylight saving time (summer/winter).
# TYPE local_hour gauge
local_hour{timezone="Europe/Madrid"} 13.0
local_hour{timezone="Europe/London"} 12.0
local_hour{timezone="America/New_York"} 7.0

# HELP timezone_utc_offset Current UTC offset in the specified timezone, formatted as "UTC+HH" or "UTC-HH".
# TYPE timezone_utc_offset gauge
timezone_utc_offset{timezone="Europe/Madrid",utc_offset="UTC+02"} 2.0
timezone_utc_offset{timezone="Europe/London",utc_offset="UTC+01"} 1.0
timezone_utc_offset{timezone="America/New_York",utc_offset="UTC-04"} -4.0
...
```

This output includes the local hour and the UTC offset for all timezones globally, identified by their respective `timezone` and `utc_offset` labels.

## Deploy on local

To run this script, you need Python 3 and `pip` installed on your system.

1. Clone the repository.
2. Create a virtual environment: `python3 -m venv env`
3. Activate the virtual environment:
   - macOS/Linux: `source env/bin/activate`
   - Windows: `env\\Scripts\\activate`
4. Install the dependencies: `pip3 install -r requirements.txt`
5. Run the software `python timeExporter.py`
5. When you finish, do not forget to deactivate the virtual environment: `deactivate`

## Deploy on kubernetes
## Prerequisites

- [Kubernetes](https://kubernetes.io/) 1.19+
- [Helm](https://helm.sh/) 3.0+
- [Prometheus](https://prometheus.io/)

## Installation

### Step 1: Configure Values

Edit the `values.yaml` file inside chart directory to customize the configuration of the global time exporter. Important configuration values include:

```yaml
name: time-exporter
namespace: monitoring
replicas: 1

image:
  repository: xxxx
  tag: v0.1.0
  pullPolicy: Always

containerPort: 8000

deployment:
  create: true

service:
  create: true
  type: ClusterIP
  port: 8000
  protocol: TCP

serviceMonitor:
  create: true
  path: "/metrics"
  interval: 60s
```

### Step 2: Deploy to Kubernetes

Use Helm to install the chart in your Kubernetes cluster.

```bash
helm install time-exporter ./chart
```

This will create all necessary resources, including the `Deployment`, `Service`, and (optionally) a `ServiceMonitor` for Prometheus Operator integration.

### Helm Chart Configuration

The Helm chart includes the following main configuration options:

- **name**: Base name for all Kubernetes resources.
- **namespace**: Kubernetes namespace for resource deployment.
- **replicas**: Number of replicas for the time-exporter deployment.
- **image.repository**: ECR repository for the time-exporter image.
- **image.tag**: Tag of the image to be used.
- **image.pullPolicy**: Image pull policy (`Always`, `IfNotPresent`, or `Never`).
- **containerPort**: Port on which the container listens.
- **deployment.create**: Flag to enable/disable deployment creation.
- **service.create**: Flag to enable/disable service creation.
- **service.type**: Kubernetes service type (e.g., `ClusterIP`).
- **service.port**: Port exposed by the service.
- **serviceMonitor.create**: Flag to enable/disable ServiceMonitor creation for Prometheus.
- **serviceMonitor.path**: HTTP path for metrics scraping.
- **serviceMonitor.interval**: Interval for Prometheus to scrape metrics.


## Accessing Metrics in Prometheus

Once deployed, Prometheus can access the metrics exposed by the exporter. Ensure that Prometheus is configured to scrape metrics from this service, either directly or through the `ServiceMonitor` if you are using the Prometheus Operator.

## Uninstallation

To remove the global time exporter from your Kubernetes cluster:

```bash
helm uninstall time-exporter
```

This command will delete all resources created by the chart.

---
### Adding Custom Timezones

By default, the script exports metrics for all timezones provided by the `pytz` library. If you want to limit the timezones or customize them, uncomment and modify the first `timezones` list in the script and comment the second timezones list:

```python
timezones = ['Europe/Madrid', 'Europe/London', 'America/New_York']  # Add or remove timezones here
```

Simply replace this list with the timezones you want to monitor.

---
## License

This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
