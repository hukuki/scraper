# Scraper Framework

This repository consists of tools for scraping. It provides abstract classes that
are ready to extend for scraping any govermental website that hosts documents.

### Document format 

<code>
{
    "createdAt" : "The first time this document is retrieved",
    "updatedAt" : "The time this document last updated", 
    "doc" : {
        "content": "base64 encoded document string. can be any file type.",
        ...
    }
    "doc_name" : "Name of the document" 
}
</code>
