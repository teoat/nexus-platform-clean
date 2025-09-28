import React from "react";
import { Handle, Position, NodeProps } from "reactflow";

const SubWorkflowNode: React.FC<NodeProps> = ({ data }) => {
  return (
    <div className="workflow-node-content">
      <div className="workflow-node-label">{data.label}</div>
      <div className="workflow-node-config">
        {data.config?.sub_workflow_id &&
          `Workflow: ${data.config.sub_workflow_id.substring(0, 15)}...`}
      </div>
      <Handle
        type="target"
        position={Position.Top}
        id="input"
        style={{ background: "#40a9ff" }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="output"
        style={{ background: "#40a9ff" }}
      />
    </div>
  );
};

export default SubWorkflowNode;
