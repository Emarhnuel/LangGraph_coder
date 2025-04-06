from typing import List, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DocumentationCrawlerInput(BaseModel):
    """Input schema for DocumentationCrawlerTool."""

    urls: List[str] = Field(
        ...,
        description="List of documentation URLs to crawl and process.",
    )
    output_dir: str = Field(
        ...,
        description="Directory to save the processed markdown files.",
    )
    max_depth: int = Field(
        1,
        description="Maximum depth for deep crawling from initial URLs. Set to 0 to disable deep crawling.",
    )
    concurrency: int = Field(
        5,
        description="Number of concurrent requests to make during crawling.",
    )
    cache_mode: str = Field(
        "disk",
        description="Caching mode to use: 'memory', 'disk', or 'none'.",
    )
    fit_for_llm: bool = Field(
        True,
        description="Whether to optimize the markdown for LLM processing.",
    )


class DocumentationCrawlerTool(BaseTool):
    name: str = "documentation_crawler"
    description: str = (
        "Crawls and processes documentation URLs, extracting content including text, "
        "code examples, and diagrams. Converts the content to well-structured markdown "
        "files and saves them to the specified output directory. Can process multiple "
        "URLs concurrently and discover related documentation pages through deep crawling."
    )
    args_schema: Type[BaseModel] = DocumentationCrawlerInput

    def _run(
        self,
        urls: List[str],
        output_dir: str,
        max_depth: int = 1,
        concurrency: int = 5,
        cache_mode: str = "disk",
        fit_for_llm: bool = True,
    ) -> str:
        """Execute the documentation crawling and processing.
        
        Args:
            urls: List of documentation URLs to crawl and process
            output_dir: Directory to save the processed markdown files
            max_depth: Maximum depth for deep crawling from initial URLs
            concurrency: Number of concurrent requests to make during crawling
            cache_mode: Caching mode to use ('memory', 'disk', or 'none')
            fit_for_llm: Whether to optimize the markdown for LLM processing
            
        Returns:
            A summary of the crawling and processing results
        """
        try:
            # Import Crawl4AI here to avoid dependency requirements for those not using this tool
            from crawl4ai import AsyncWebCrawler
            import asyncio
            import os
            import json
            from datetime import datetime
            
            # Ensure the output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Create a crawler instance
            crawler = AsyncWebCrawler(
                use_cache=cache_mode != "none",
                cache_mode=cache_mode if cache_mode != "none" else "memory",
                max_depth=max_depth,
                concurrency=concurrency
            )
            
            # Run the crawler asynchronously
            results = asyncio.run(crawler.arun_many(urls))
            
            # Process and save the results
            processed_files = []
            summary = {
                "total_urls": len(urls),
                "successful": 0,
                "failed": 0,
                "processed_files": []
            }
            
            for i, result in enumerate(results):
                if result.success:
                    # Generate a filename from the URL
                    filename = f"doc_{i+1}.md"
                    filepath = os.path.join(output_dir, filename)
                    
                    # Get markdown content
                    markdown_content = result.get_markdown(fit_for_llm=fit_for_llm)
                    
                    # Add URL reference at the top of the markdown
                    markdown_content = f"# Source: {result.url}\n\n{markdown_content}"
                    
                    # Save the markdown file
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(markdown_content)
                    
                    # Save metadata file
                    metadata_path = os.path.join(output_dir, f"doc_{i+1}_metadata.json")
                    metadata = {
                        "url": result.url,
                        "title": result.title or "Unknown",
                        "crawl_time": datetime.now().isoformat(),
                        "status_code": result.status_code,
                    }
                    
                    with open(metadata_path, "w", encoding="utf-8") as f:
                        json.dump(metadata, f, indent=2)
                    
                    processed_files.append(filepath)
                    summary["successful"] += 1
                    summary["processed_files"].append({
                        "url": result.url,
                        "file": filepath
                    })
                else:
                    summary["failed"] += 1
            
            # Generate and save the summary
            summary_path = os.path.join(output_dir, "crawl_summary.json")
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            
            # Return a human-readable summary
            return f"Crawling complete. Successfully processed {summary['successful']} out of {len(urls)} URLs. " \
                   f"Created {len(processed_files)} markdown files in '{output_dir}'."
                   
        except ImportError:
            return "Error: Crawl4AI is not installed. Please install it with 'pip install crawl4ai'."
        except Exception as e:
            return f"Error during crawling: {str(e)}"
