package controller

import (
	"context"

	"sigs.k8s.io/controller-runtime/pkg/log"

	maestrov1alpha1 "github.com/ai4quantum/maestro/api/v1alpha1"
	"k8s.io/apimachinery/pkg/api/meta"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	ctrl "sigs.k8s.io/controller-runtime"
)

// ConditionStatus defines WorkflowRun condition status.
type ConditionStatus string

// Defines WorkflowRun condition status.
const (
	TypeAvailable   ConditionStatus = "Available"
	TypeProgressing ConditionStatus = "Progressing"
	TypeCompleted   ConditionStatus = "Completed"
	TypeFailed      ConditionStatus = "Failed"
)

// GetWorkflowRun gets the WorkflowRun from api server.
func (r *WorkflowRunReconciler) GetWorkflowRun(ctx context.Context, req ctrl.Request, workflowrun *maestrov1alpha1.WorkflowRun) error {
	err := r.Get(ctx, req.NamespacedName, workflowrun)
	if err != nil {
		return err
	}

	return nil
}

// SetInitialCondition sets the status condition of the WorkflowRun to available initially
// when no condition exists yet.
func (r *WorkflowRunReconciler) SetInitialCondition(ctx context.Context, req ctrl.Request, workflowrun *maestrov1alpha1.WorkflowRun) error {
	if workflowrun.Status.Conditions != nil || len(workflowrun.Status.Conditions) != 0 {
		return nil
	}

	err := r.SetCondition(ctx, req, workflowrun, TypeAvailable, "Starting reconciliation")

	return err
}

// SetCondition sets the status condition of the WorkflowRun.
func (r *WorkflowRunReconciler) SetCondition(
	ctx context.Context, req ctrl.Request,
	workflowrun *maestrov1alpha1.WorkflowRun, condition ConditionStatus,
	message string,
) error {
	log := log.FromContext(ctx)

	meta.SetStatusCondition(
		&workflowrun.Status.Conditions,
		metav1.Condition{
			Type:   string(condition),
			Status: metav1.ConditionUnknown, Reason: "Reconciling",
			Message: message,
		},
	)

	if err := r.Status().Update(ctx, workflowrun); err != nil {
		log.Error(err, "Failed to update WorkflowRun status")

		return err
	}

	if err := r.Get(ctx, req.NamespacedName, workflowrun); err != nil {
		log.Error(err, "Failed to re-fetch WorkflowRun")

		return err
	}

	return nil
}
