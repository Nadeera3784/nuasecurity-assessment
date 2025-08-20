import { CircleDollarSign, PlusIcon } from "lucide-react";
import { Button } from "../ui/button";
import { StatisticsProps } from "@/interfaces";

export default function statistics({ setShowDialog }: StatisticsProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <CircleDollarSign className="w-5 h-5 text-green-500" />
          <div className="flex items-center space-x-2">
            <p className="font-semibold text-gray-900">Subscription 01</p>
            <p className="text-sm text-gray-600">Ends Aug 23, 2025</p>
          </div>
        </div>
        <div className="flex items-center">
          <div className="h-16 w-px bg-gray-300" />
          <div className="text-center px-8">
            <div className="flex items-center space-x-1 mb-1">
              <span className="text-sm text-gray-600">Available</span>
              <svg
                className="w-4 h-4 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <circle cx={12} cy={12} r={10} />
                <path d="M9,9h6v6H9V9z" />
              </svg>
            </div>
            <p className="text-2xl font-bold text-green-600">8,000 SAR</p>
          </div>
          <div className="h-16 w-px bg-gray-300" />
          <div className="text-center px-8">
            <div className="flex items-center space-x-1 mb-1">
              <span className="text-sm text-gray-600">Consumed</span>
              <svg
                className="w-4 h-4 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <circle cx={12} cy={12} r={10} />
                <path d="M9,9h6v6H9V9z" />
              </svg>
            </div>
            <p className="text-2xl font-bold text-gray-500">400 SAR</p>
          </div>
          <div className="h-16 w-px bg-gray-300" />
          <div className="text-center px-8">
            <div className="mb-1">
              <span className="text-sm text-gray-600">Total Balance</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">1,200 SAR</p>
          </div>
        </div>
        <Button className="cursor-pointer" onClick={() => setShowDialog(true)}>
          <PlusIcon className="h-4 w-4 mr-2" />
          Create Program
        </Button>
      </div>
    </div>
  );
}
