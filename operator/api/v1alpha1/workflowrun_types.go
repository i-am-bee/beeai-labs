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

package v1alpha1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// WorkflowRun
type WorkflowRunSpec struct {
	// Important: Run "make" to regenerate code after modifying this file

	Agents   []string `json:"agents,omitempty"`
	Workflow string   `json:"workflow,omitempty"`
	LogLevel string   `json:"loglevel,omitempty"`
}

type WorkflowRunStatus struct {
	// INSERT ADDITIONAL STATUS FIELD - define observed state of cluster
	// Important: Run "make" to regenerate code after modifying this file
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status

type WorkflowRun struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   WorkflowRunSpec   `json:"spec,omitempty"`
	Status WorkflowRunStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true

type WorkflowRunList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []WorkflowRun `json:"items"`
}

// Workflow

type Input struct {
	Prompt   string `json:"prompt,omitempty"`
	Template string `json:"template,omitempty"`
}
type Loop struct {
	Agent  string `json:"agent,omitempty"`
	Until string `json:"until,omitempty"`
}
type Condition struct {
	If      string `json:"if,omitempty"`
	Then    string `json:"then,omitempty"`
	Else    string `json:"else,omitempty"`
	Case    string `json:"case,omitempty"`
	Do      string `json:"do,omitempty"`
	Default string `json:"default,omitempty"`
}
//type Parallel struct {
//	Agent string `json:"agent,omitempty"` // ???
//}
type Step struct {
	Name      string      `json:"name,omitempty"`
	Agent     string      `json:"agent,omitempty"`
	Input     Input       `json:"input,omitempty"`
	Loop      Loop        `json:"loop,omitempty"`
	Condition []Condition `json:"condition,omitempty"`
	Parallel  []string  `json:"parallel,omitempty"`
}
type Exception struct {
	Name  string `json:"name,omitempty"`
	Agent string `json:"agent,omitempty"`
}

type Event struct {
	Cron  string   `json:"cron,omitempty"`
	Name  string   `json:"name,omitempty"`
	Agent string   `json:"agent,omitempty"`
	Steps []string `json:"steps,omitempty"`
	Exit  string   `json:"exit,omitempty"`
}

type Template struct {
	// Important: Run "make" to regenerate code after modifying this file
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Event     Event     `json:"event,omitempty"`
	Agents    []string  `json:"agents,omitempty"`
	Exception Exception `json:"exception,omitempty"`
	Prompt    string    `json:"prompt,omitempty"`
	Steps     []Step    `json:"steps,omitempty"`
}

type WorkflowSpec struct {
	Template Template `json:"template,omitempty"`
}

type WorkflowStatus struct {
	// INSERT ADDITIONAL STATUS FIELD - define observed state of cluster
	// Important: Run "make" to regenerate code after modifying this file
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status

type Workflow struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   WorkflowSpec   `json:"spec,omitempty"`
	Status WorkflowStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true

type WorkflowList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []Workflow `json:"items"`
}

// Agent
type AgentSpec struct {
	// Important: Run "make" to regenerate code after modifying this file

	Description  string   `json:"description,omitempty"`
	Model        string   `json:"model,omitempty"`
	Framework    string   `json:"framework,omitempty"`
	Mode         string   `json:"mode,omitempty"`
	Tools        []string `json:"tools,omitempty"`
	Instructions string   `json:"instructions,omitempty"`
	Code         string   `json:"code,omitempty"`
	Input        string   `json:"input,omitempty"`
	Output       string   `json:"oputput,omitempty"`
	Url          string   `json:"url,omitempty"`
}

type AgentStatus struct {
	// INSERT ADDITIONAL STATUS FIELD - define observed state of cluster
	// Important: Run "make" to regenerate code after modifying this file
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status

type Agent struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   AgentSpec   `json:"spec,omitempty"`
	Status AgentStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true

type AgentList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []Agent `json:"items"`
}

func init() {
	SchemeBuilder.Register(&WorkflowRun{}, &WorkflowRunList{})
	SchemeBuilder.Register(&Workflow{}, &WorkflowList{})
	SchemeBuilder.Register(&Agent{}, &AgentList{})
}
