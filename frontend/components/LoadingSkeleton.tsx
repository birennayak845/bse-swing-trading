export default function LoadingSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((i) => (
        <div
          key={i}
          className="border border-gray-200 dark:border-gray-800 rounded-lg p-4 animate-pulse"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 flex-1">
              <div className="w-6 h-6 bg-gray-200 dark:bg-gray-800 rounded" />
              <div className="flex-1">
                <div className="h-5 w-48 bg-gray-200 dark:bg-gray-800 rounded mb-2" />
                <div className="h-3 w-24 bg-gray-200 dark:bg-gray-800 rounded" />
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="h-3 w-12 bg-gray-200 dark:bg-gray-800 rounded mb-1" />
                <div className="h-4 w-16 bg-gray-200 dark:bg-gray-800 rounded" />
              </div>
              <div className="text-right">
                <div className="h-3 w-12 bg-gray-200 dark:bg-gray-800 rounded mb-1" />
                <div className="h-4 w-16 bg-gray-200 dark:bg-gray-800 rounded" />
              </div>
              <div className="h-6 w-12 bg-gray-200 dark:bg-gray-800 rounded" />
              <div className="w-5 h-5 bg-gray-200 dark:bg-gray-800 rounded" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
