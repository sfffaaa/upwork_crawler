# upwork_crawler
Crawl upwork website for further analysis

This project focus on upwork website in order to analysis attributes which developers have and try to find some insight of that.

There are some notes here when develope this project.
1. Use selenium instead of requests
	When using requests/curl, the website will show javascript engine is required, so that's why I change to selenium. It seems upwork use angular to implement their website. Besides, firefox is used due to the error occuring on phatomjs and chrome. But I ignore this problem for shorten time of implement.

2. Avoid ban by website
	The easist mechanism, sleeping and crawl, is applied. However, it spends lot of time about sleeping. Maybe the proxy mechanism will be implemented at future.

How to run
1. Install all the python module
2. Make sure you have firefox
3. Adjust parameter inside the upwork.py
4. Run "python upwork.py"
5. The result with json format is stored inside result folder.

However, I don't test whether it is runable on other system (different version os or different system), so if there are any problem, just let me know.
