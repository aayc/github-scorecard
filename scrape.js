const { Octokit } = require("@octokit/core");
const fs = require('fs');
var tqdm = require('ntqdm')();
const auth_token = process.env["GITHUB_AUTH_TOKEN"]
const octokit = new Octokit({ auth: auth_token });

async function fetchRepos(order="desc", pages=5) {
	const results = []
	for (const page of [...Array(pages).keys()]) {
		console.log("Page " + page)
		const res = await octokit.request('GET /search/repositories', {
			q: 'language:python',
			sort: "stars",
			order: order,
			per_page: 100,
			page: page
		})
		results.push(...res.data.items)
	}
	return results
}

(async () => {
	const bigStars = await fetchRepos("desc")
	const smallStars = await fetchRepos("asc")
	const allStars = bigStars.concat(smallStars)
	fs.writeFileSync("repos.json", JSON.stringify(allStars, null, 2))
})();
