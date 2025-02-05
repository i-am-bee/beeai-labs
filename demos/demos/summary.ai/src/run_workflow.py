#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys
import yaml
import dotenv
from step import Step
from utils import run_agent 

dotenv.load_dotenv()

def parse_yaml(file_path):
    """Loads workflow definition from YAML."""
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

def sequential_workflow(workflow):
    """Executes agents sequentially as defined in the workflow."""
    prompt = workflow["spec"]["prompt"]
    steps = workflow["spec"]["steps"]

    for step_config in steps:
        step = Step(step_config)

        if step_config["agent"] == "summary_agent":
            prompt = "Create a summary using only LLM tool based on the following text: We introduce Super Quantum Mechanics (SQM) as a theory that considers states in Hilbert space subject to multiple quadratic constraints. Traditional quantum mechanics corresponds to a single quadratic constraint of wavefunction normalization. In its simplest form, SQM considers states in the form of unitary operators, where the quadratic constraints are conditions of unitarity. In this case, the stationary SQM problem is a quantum inverse problem with multiple applications in machine learning and artificial intelligence. The SQM stationary problem is equivalent to a new algebraic problem that we address in this paper. The SQM non-stationary problem considers the evolution of a quantum system, distinct from the explicit time dependence of the Hamiltonian, H(t). Several options for the SQM dynamic equation are considered, and quantum circuits of 2D type are introduced, which transform one quantum system into another. Although no known physical process currently describes such dynamics, this approach naturally bridges direct and inverse quantum mechanics problems, allowing for the development of a new type of computer algorithm. Beyond computer modeling, the developed theory could be directly applied if or when a physical process capable of solving an inverse quantum problem in a single measurement act (analogous to wavefunction measurement in traditional quantum mechanics) is discovered in the future. I. INTRODUCTION Traditional quantum mechanics involves the time evolution of a wavefunction |ψ⟩ (a unit-length vector) in Hilbert space. iℏ ∂ψ ∂t = Hψ (1) A generalization of this dynamics defines a quantum channel, which is considered as a trace-preserving positive map. The simplest example of such a channel is a unitary mapping. A_OUT = U A_IN U † For the Schrödinger equation (1), the unitary operator U U = exp i t ℏ H(3) ψ (t) E = U ψ (0)E (4) defines a quantum channel (2) that describes the time evolution of the initial state ψ (0), this can be expressed by setting U = U and A_IN = ψ (0) ψ (0). The most commonly studied quantum channel is the one that describes the evolution of a quantum system between t and t + τ. If the system has a time-independent Hamiltonian H, the evolution over a finite time can be obtained through multiple applications of the quantum channel that describes the time evolution over a small interval τ. The time dependence of this quantum channel may arise solely from the explicit time dependence of the Hamiltonian, H(t). In this work, we generalize the system state from a unit-length vector |ψ⟩ to a unitary operator U, or, in the case of a mixed state, from a density matrix to a mixed unitary channel. We assume that the quantum channel can exhibit its own dynamics, possibly described by a non-stationary equation, with a solution in the form of a time-dependent unitary operator that generates a time-dependent quantum channel. While no known physical process is currently described by such dynamics, this approach naturally bridges direct and inverse quantum mechanics problems and provides valuable insights into machine learning and artificial intelligence. Aside from computer modeling, the developed theory will have direct applications if a physical process capable of solving an inverse quantum problem is discovered in the future. The first step in approaching this problem is to introduce a stationary Schrödinger-like equation that describes a quantum inverse problem. In Appendix D: A Numerical Solution to Quadratic Form Maximization Problem in Unitary Matrix Space of Ref. we formulated and later solved the quantum inverse problem. For a given sequence of observations l = 1 ... M, of pure (5) or mixed states (6) mapping, ψ (l) → ϕ (l) (5) ϱ (l) → ρ (l) (6) the goal is to reconstruct the unitary operator U (2) that optimally maps A_IN = ψ (l) ψ (l) to A_OUT = ϕ (l) ϕ (l), or for mixed states, A_IN = ρ (l) to A_OUT = ϱ (l) for all l = 1 ... M. By interpreting l as time t (where l → l + 1 corresponds to t → t + τ), the time evolution of a quantum system, ψ (l) → ψ (l+1), or, for mixed states, ρ (l) → ρ (l+1), can be described by setting ϕ (l) = ψ (l+1) or ϱ (l) = ρ (l+1), respectively. This reconstruction can then be used to obtain the Hamiltonian by taking the logarithm of the unitary matrix U. There is no unique solution to Eq. (7); many different Hamiltonians can be used to implement a quantum gate U. H = i ℏ τ ln U (7) Our approach is applicable when the objective function F (typically the total fidelity of the mapping) can be represented as a quadratic form in the unitary operator U. F = D X−1 j,j′=0 nX−1 k,k′=0 U ∗ jkSjk;j ′k′Uj ′k′ This is especially simple for pure state mappings, when (assuming, for now, that all ω (l) = 1), F = X M l=1 ω (l) D ϕ (l) U ψ (l) E 2 (9) is a quadratic function of U, which gives a simple expression. Sjk;j ′k′ = X M l=1 ω (l)ϕ (l)∗ j ϕ (l) j ′ ψ (l)∗ k ψ (l) k′ (10) For mixed state mappings (6), the expression for the total fidelity F involvesSjk;j ′k′ = X M l=1 ω (l) ϱe (l)∗ jj′ ρe (l)∗ kk′ (11)where ϱe and ρe are simple functions of ϱ and ρ. For example, to obtain the fidelity of mixed state unitary mapping, one needs to consider the mapping √ρ → √ϱ, since for a unitary quantum channel, the same quantum channel transforms both ρ and √ρ. For a dynamic system where ϱ (l) = ρ (l+1), the calculation of Sjk;j ′k′ is effectively reduced to an autocorrelation with a delay of τ.Sjk;j ′k′ = X M l=1 ω (l) ρe (l+1)∗ jj′ ρe (l)∗ kk′ (12)If it were a classical system, this calculation would be equivalent to computing a time-average. In quantum systems, however, the situation is more complex since the measurement of ρ (l) destroys the state, making ρ (l+1) at the next step potentially unavailable. Recently, new approaches have been developed that allow for the measurement of even multiple-time autocorrelations in quantum systems. This way, the Sjk;j ′k′ is obtained from the single-time density matrix autocorrelation by continuous observation of the system state. Alternatively, instead of continuous observation of the system state, one can obtain the Sjk;j ′k′ using a process typical for quantum computations.In quantum computations, an initial state ψ (0) is prepared in a specific state of qubits. Then, a unitary transformation corresponding to the required quantum circuit is applied, and the result is measured. Similarly, we can create ψ (0) randomly and measure the result ψ (τ) of the system’s evolution. In this approach, instead of continuous observation of the system, we randomly create the initial state M times and measure the result of its evolution. This process may be easier to implement than continuous observation of a quantum system’s state. The goal is to find the operator U that maximizes the fidelity. In the case of perfect matching, this results in a fidelity equal to the number of observations, F = M, when ω (l) = 1. This paper is accompanied by software which is available from Ref.; all references to code in the paper correspond to this software."
            prompt = step.run(prompt)["prompt"]
        else:
            prompt = step.run(prompt)["prompt"]  # Pass output to the next step

    return prompt

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_workflow.py <yaml_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    workflow_yaml = parse_yaml(file_path)

    if workflow_yaml["spec"]["strategy"]["type"] == "sequence":
        result = sequential_workflow(workflow_yaml)
        print(f"🐝 Final Output: {result}")
    else:
        raise ValueError("Invalid workflow strategy type")
