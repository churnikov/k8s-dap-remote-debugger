{{- define "k8s-remote-debugger.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "k8s-remote-debugger.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- include "k8s-remote-debugger.name" . -}}
{{- end -}}
{{- end -}}

{{- define "k8s-remote-debugger.labels" -}}
app.kubernetes.io/name: {{ include "k8s-remote-debugger.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{- end -}}

{{- define "k8s-remote-debugger.selectorLabels" -}}
app.kubernetes.io/name: {{ include "k8s-remote-debugger.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
