/*
Copyright 2025.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package controller

import (
	"context"
	apierrors "k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"
	"time"

	maestrov1alpha1 "github.com/ai4quantum/maestro/api/v1alpha1"
)

// WorkflowRunReconciler reconciles a WorkflowRun object
type WorkflowRunReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

const (
	// minute
	DefaultReconciliationInterval = 5
)

// +kubebuilder:rbac:groups=maestro.ai4quantum.com,resources=workflowruns,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=maestro.ai4quantum.com,resources=workflowruns/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=maestro.ai4quantum.com,resources=workflowruns/finalizers,verbs=update

// Reconcile is part of the main kubernetes reconciliation loop which aims to
// move the current state of the cluster closer to the desired state.
// TODO(user): Modify the Reconcile function to compare the state specified by
// the WorkflowRun object against the actual cluster state, and then
// perform operations to make the cluster state reflect the state specified by
// the user.
//
// For more details, check Reconcile and its Result here:
// - https://pkg.go.dev/sigs.k8s.io/controller-runtime@v0.19.0/pkg/reconcile
func (r *WorkflowRunReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	logger := log.FromContext(ctx)
	logger.Info("hey!")

	workflowrun := &maestrov1alpha1.WorkflowRun{}
	err := r.Get(ctx, req.NamespacedName, workflowrun)
	if err != nil {
		if apierrors.IsNotFound(err) {
			logger.Info("WorkflowRun resource not found. Ignoring since object must be deleted")
			return ctrl.Result{}, nil
		}
		logger.Error(err, "Failed to get WorkflowRun")
		return ctrl.Result{}, err
	}
	logger.Info(workflowrun.Name)
	// Try to set initial condition status
	err = r.SetInitialCondition(ctx, req, workflowrun)
	if err != nil {
		logger.Error(err, "failed to set initial condition")
		return ctrl.Result{}, err
	}

	// Deployment if not exist
	ok, err := r.DeploymentIfNotExist(ctx, req, workflowrun)
	if err != nil {
		logger.Error(err, "failed to deploy deployment for Workflow")
		return ctrl.Result{}, err
	}

	if ok {
		return ctrl.Result{RequeueAfter: time.Minute}, nil
	}
	logger.Info("ending reconciliation")
	return ctrl.Result{RequeueAfter: time.Duration(time.Minute * time.Duration(DefaultReconciliationInterval))}, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *WorkflowRunReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&maestrov1alpha1.WorkflowRun{}).
		Complete(r)
}
