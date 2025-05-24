package controller

import (
	"context"
	"fmt"
	"gopkg.in/yaml.v3"
	"os"

	maestrov1alpha1 "github.com/ai4quantum/maestro/api/v1alpha1"
	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/log"

	apierrors "k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/apimachinery/pkg/types"
	"k8s.io/apimachinery/pkg/util/intstr"
	"k8s.io/client-go/dynamic"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
)

// +kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups="",resources=services,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups="",resources=configmaps,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=maestro.ai4quantum.com,resources=workflows,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=maestro.ai4quantum.com,resources=agents,verbs=get;list;watch;create;update;patch;delete

func (r *WorkflowRunReconciler) Deployment(
	ctx context.Context, req ctrl.Request,
	workflowrun *maestrov1alpha1.WorkflowRun,
) (*appsv1.Deployment, error) {
	log := log.FromContext(ctx)

	kubeconfigPath := os.Getenv("KUBECONFIG")
	if kubeconfigPath == "" {
		kubeconfigPath = "~/.kube/config"
	}
	config, err := clientcmd.BuildConfigFromFlags("", kubeconfigPath)
	if err != nil {
		// Fallback to in-cluster config if KUBECONFIG is not set or invalid
		config, err = rest.InClusterConfig()
		if err != nil {
			return nil, err
		}
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		log.Error(err, "failed creating clientset")
		return nil, err
	}

	// Create the Service
	service := &corev1.Service{
		ObjectMeta: metav1.ObjectMeta{
			Name:      workflowrun.Name,
			Namespace: workflowrun.Namespace,
		},
		Spec: corev1.ServiceSpec{
			Selector: map[string]string{"app.kubernetes.io/instance": workflowrun.Name},
			Ports: []corev1.ServicePort{
				{
					Protocol: corev1.ProtocolTCP,
					Port:     80,
					TargetPort: intstr.IntOrString{
						Type:   intstr.Int,
						IntVal: 5000,
					},
					// NodePort: 30051,
				},
			},
			// Type: corev1.ServiceTypeNodePort,
		},
	}
	// Set NodePort
	if workflowrun.Spec.NodePort != 0 {
		service.Spec.Type = corev1.ServiceTypeNodePort
		service.Spec.Ports[0].NodePort = int32(workflowrun.Spec.NodePort)
	}

	if err := ctrl.SetControllerReference(workflowrun, service, r.Scheme); err != nil {
		log.Error(err, "failed to set controller owner reference")
		return nil, err
	}

	_, err = clientset.CoreV1().Services("default").Create(context.TODO(), service, metav1.CreateOptions{})
	if err != nil {
		log.Error(err, "failed creating service")
		return nil, err
	}

	// Create ConfigMap of workflow and agent definition
	// Workflow
	yamlData, err := r.ReadCR(ctx, req, workflowrun, "workflows", workflowrun.Spec.Workflow)
	if err != nil {
		return nil, err
	}
	data := make(map[string]string)
	data["workflow"] = string(yamlData)

	// Agents
	agentYamlData := ""
	for _, agent := range workflowrun.Spec.Agents {
		yamlData, err := r.ReadCR(ctx, req, workflowrun, "agents", agent)
		if err != nil {
			return nil, err
		}
		agentYamlData = agentYamlData + "---\n" + yamlData
	}
	data["agents"] = string(agentYamlData)

	configMap := &corev1.ConfigMap{
		ObjectMeta: metav1.ObjectMeta{
			Name:      workflowrun.Name, // Name of your ConfigMap
			Namespace: workflowrun.Namespace,
		},
		Data: data,
	}
	if err := ctrl.SetControllerReference(workflowrun, configMap, r.Scheme); err != nil {
		log.Error(err, "failed to set controller owner reference")
		return nil, err
	}

	_, err = clientset.CoreV1().ConfigMaps("default").Create(context.TODO(), configMap, metav1.CreateOptions{})
	if err != nil {
		log.Error(err, "failed creating configmap")
		// return nil, err
	}

	// Create the workflow deployment
	labels := map[string]string{
		"app.kubernetes.io/name":       "WorkflowRun",
		"app.kubernetes.io/instance":   workflowrun.Name,
		"app.kubernetes.io/version":    "v1alpha1",
		"app.kubernetes.io/part-of":    "workflow-operator",
		"app.kubernetes.io/created-by": "controller-manager",
	}
	replicas := int32(1)

	dep := &appsv1.Deployment{
		ObjectMeta: metav1.ObjectMeta{
			Name:      workflowrun.Name,
			Namespace: workflowrun.Namespace,
		},
		Spec: appsv1.DeploymentSpec{
			Replicas: &replicas,
			Selector: &metav1.LabelSelector{
				MatchLabels: labels,
			},
			Template: corev1.PodTemplateSpec{
				ObjectMeta: metav1.ObjectMeta{
					Labels: labels,
				},
				Spec: corev1.PodSpec{
					Containers: []corev1.Container{{
						Image:           "localhost/maestro-engine:latest",
						Name:            workflowrun.Name,
						ImagePullPolicy: corev1.PullIfNotPresent,
						Ports: []corev1.ContainerPort{{
							ContainerPort: int32(5000),
							Name:          "workflow",
						}},
						VolumeMounts: []corev1.VolumeMount{
							{
								Name:      "workflow",
								MountPath: "/etc/config",
							},
						},
					}},
					Volumes: []corev1.Volume{
						{
							Name: "workflow",

							VolumeSource: corev1.VolumeSource{
								ConfigMap: &corev1.ConfigMapVolumeSource{
									LocalObjectReference: corev1.LocalObjectReference{
										Name: workflowrun.Name,
									},
								},
							},
						},
					},
				},
			},
		},
	}
	if workflowrun.Spec.Environments != "" {
		env := corev1.EnvFromSource{
			ConfigMapRef: &corev1.ConfigMapEnvSource{
				LocalObjectReference: corev1.LocalObjectReference{
					Name: workflowrun.Spec.Environments,
				},
			},
		}
		dep.Spec.Template.Spec.Containers[0].EnvFrom = append(dep.Spec.Template.Spec.Containers[0].EnvFrom, env)
	}

	if workflowrun.Spec.Secrets != "" {
		env := corev1.EnvFromSource{
			SecretRef: &corev1.SecretEnvSource{
				LocalObjectReference: corev1.LocalObjectReference{
					Name: workflowrun.Spec.Secrets,
				},
			},
		}
		dep.Spec.Template.Spec.Containers[0].EnvFrom = append(dep.Spec.Template.Spec.Containers[0].EnvFrom, env)
	}

	// Set the ownerRef for the Deployment
	// More info: https://kubernetes.io/docs/concepts/overview/working-with-objects/owners-dependents/
	if err := ctrl.SetControllerReference(workflowrun, dep, r.Scheme); err != nil {
		log.Error(err, "failed to set controller owner reference")
		return nil, err
	}

	return dep, nil
}

func (r *WorkflowRunReconciler) DeploymentIfNotExist(
	ctx context.Context, req ctrl.Request,
	workflowrun *maestrov1alpha1.WorkflowRun,
) (bool, error) {
	log := log.FromContext(ctx)

	dep := &appsv1.Deployment{}

	err := r.Get(ctx, types.NamespacedName{Name: workflowrun.Name, Namespace: workflowrun.Namespace}, dep)
	if err != nil && apierrors.IsNotFound(err) {
		dep, err := r.Deployment(ctx, req, workflowrun)
		if err != nil {
			log.Error(err, "Failed to define new Deployment resource for Workflow")

			err = r.SetCondition(
				ctx, req, workflowrun, TypeAvailable,
				fmt.Sprintf("Failed to create Deployment for Workflow (%s): (%s)", workflowrun.Name, err),
			)
			if err != nil {
				return false, err
			}
		}

		log.Info(
			"Creating a new Deployment",
			"Deployment.Namespace", dep.Namespace,
			"Deployment.Name", dep.Name,
		)

		err = r.Create(ctx, dep)
		if err != nil {
			log.Error(
				err, "Failed to create new Deployment",
				"Deployment.Namespace", dep.Namespace,
				"Deployment.Name", dep.Name,
			)

			return false, err
		}

		err = r.GetWorkflowRun(ctx, req, workflowrun)
		if err != nil {
			log.Error(err, "Failed to re-fetch WorkflowRun")
			return false, err
		}

		err = r.SetCondition(
			ctx, req, workflowrun, TypeProgressing,
			fmt.Sprintf("Created Deployment for the Workflow: (%s)", workflowrun.Name),
		)
		if err != nil {
			return false, err
		}

		return true, nil
	}

	if err != nil {
		log.Error(err, "Failed to get Deployment")

		return false, err
	}

	return false, nil
}

// Read Workflow or Agent custom resource instances
func (r *WorkflowRunReconciler) ReadCR(
	ctx context.Context, req ctrl.Request,
	workflowrun *maestrov1alpha1.WorkflowRun,
	resourceType string,
	resourceName string,
) (string, error) {
	log := log.FromContext(ctx)

	kubeconfigPath := os.Getenv("KUBECONFIG")
	if kubeconfigPath == "" {
		kubeconfigPath = "~/.kube/config"
	}
	config, err := clientcmd.BuildConfigFromFlags("", kubeconfigPath)
	if err != nil {
		// Fallback to in-cluster config if KUBECONFIG is not set or invalid
		config, err = rest.InClusterConfig()
		if err != nil {
			return "", err
		}
	}

	// Create a dynamic client
	dynamicClient, err := dynamic.NewForConfig(config)
	if err != nil {
		log.Error(err, "failed creating dynamicClient")
		return "", err
	}

	// Define the GVR (Group, Version, Resource) for your custom resource
	gvr := schema.GroupVersionResource{
		Group:    "maestro.ai4quantum.com",
		Version:  "v1alpha1",
		Resource: resourceType,
	}

	// Get the custom resource instance
	namespace := workflowrun.ObjectMeta.Namespace
	name := resourceName

	unstructured, err := dynamicClient.Resource(gvr).Namespace(namespace).Get(context.TODO(), name, metav1.GetOptions{})
	if err != nil {
		log.Error(err, "failed getting "+name)
		return "", err
	}

	// Convert Unstructured to your custom resource struct
	var yamlData []byte
	if resourceType == "workflows" {
		var CRResource maestrov1alpha1.Workflow
		err = runtime.DefaultUnstructuredConverter.FromUnstructured(unstructured.Object, &CRResource)
		if err != nil {
			log.Error(err, "failed formatting resource")
			return "", err
		}

		// Marshal the custom resource to YAML
		yamlData, err = yaml.Marshal(CRResource)
		if err != nil {
			log.Error(err, "failed making yaml file")
			return "", err
		}
	} else {
		var CRResource maestrov1alpha1.Agent
		err = runtime.DefaultUnstructuredConverter.FromUnstructured(unstructured.Object, &CRResource)
		if err != nil {
			log.Error(err, "failed formatting resource")
			return "", err
		}

		// Marshal the custom resource to YAML
		yamlData, err = yaml.Marshal(CRResource)
		if err != nil {
			log.Error(err, "failed making yaml file")
			return "", err
		}
	}
	return string(yamlData), nil
}
