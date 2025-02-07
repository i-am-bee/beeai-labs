```mermaid
  flowchart LR;
      In-->LLM_Call_1;
      LLM_Call_1-->|Output_1|Gate;
      Gate-->|Pass|LLM_Call_2;
      Gate-->|Fail|Exit;
      LLM_Call_2 -->|Output_2|LLM_Call_3;
      LLM_Call_3 --> Out;