/* eslint-disable react/prop-types */
import { useState } from "react";
import { Info } from "lucide-react";

const ModalInfo = ({ title, description }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div>
      <button className="cursor-pointer" onClick={() => setIsOpen(true)}>
        <Info />
      </button>

      {isOpen && (
        <div className="fixed inset-0 px-2 z-10 overflow-hidden flex items-center justify-center">
          <div
            onClick={() => setIsOpen(false)}
            className="absolute inset-0 bg-[#030713] opacity-90"
          ></div>

          <div className="bg-white rounded-md shadow-2xl shadow-white/50 drop-shadow-2xl max-w-md w-full sm:w-96 md:w-1/2 lg:w-2/3 xl:w-1/3 z-50 max-h-[90vh] flex flex-col">
            <div className="bg-white text-black px-4 py-2 flex justify-center rounded-tl-md rounded-tr-md">
              <h2 className="text-lg font-bold tracking-tight">{title}</h2>
            </div>

            <div className="p-4 overflow-y-auto flex-grow">
              <p className="text-black tracking-tight leading-6 text-justify">
                {description}
              </p>
            </div>

            <div className="border-t px-4 py-2 flex justify-end">
              <button
                onClick={() => setIsOpen(false)}
                className="font-bold rounded-md text-white bg-[#030713] hover:bg-black px-6 py-3 mx-auto cursor-pointer"
              >
                OK
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModalInfo;
