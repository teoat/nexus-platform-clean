import React from "react";
import { Handle, Position, NodeProps } from "reactflow";

const ConditionNode: React.FC<NodeProps> = ({ data }) => {
  return (
    <div className="workflow-node-content">
      <div className="workflow-node-label">{data.label}</div>
      <div className="workflow-node-config">
        {data.config?.condition &&
          `Condition: ${data.config.condition.substring(0, 20)}...`}
      </div>
      <Handle
        type="target"
        position={Position.Top}
        id="input"
        style={{ background: "#13c2c2" }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="true"
        style={{ background: "#52c41a", left: "25%" }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="false"
        style={{ background: "#ff4d4f", left: "75%" }}
      />
    </div>
  );
};

export default ConditionNode;
