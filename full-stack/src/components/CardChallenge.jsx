import { CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

const CardChallenge = ({ id, icon, title, description, tags = [] }) => {
  return (
    <div className="max-w-sm p-6 bg-[#030710] rounded-lg shadow-sm">
      <div className="flex items-center justify-between pb-4">
        <img
          src={icon}
          alt={`Icon for ${title}`}
          className="h-8 w-8 object-contain"
        />
        <CheckCircle className="w-4 h-4 text-emerald-500" />
      </div>
      <div>
        <h5 className="mb-2 text-2xl font-semibold tracking-tight text-gray-300">
          {title}
        </h5>
      </div>
      <p className="mb-3 font-normal text-gray-500">{description}</p>
      <div className="flex flex-wrap gap-2">
        {tags?.map((tag, i) => (
          <Button className="font-base" key={i}>
            {tag}
          </Button>
        ))}
      </div>
    </div>
  );
};

export default CardChallenge;
