class Report:
    def __init__(self):
        self.metrics = {}

    def add_metrics(self, metrics):
        """Add metrics to the report."""
        self.metrics.update(metrics)

    def write_to_file(self, file_path="report.txt"):
        """Write the report to a file."""
        with open(file_path, 'w') as file:
            if "num_documents" in self.metrics:
                print(f"1. Number of documents: {self.metrics['num_documents']}", file=file)
            if "num_unique_tokens" in self.metrics:
                print(f"2. Number of unique tokens: {self.metrics['num_unique_tokens']}", file=file)
            if "index_size_kb" in self.metrics:
                print(f"3. Index size on disk: {self.metrics['index_size_kb']:.2f} KB", file=file)