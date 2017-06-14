const request = require("request")
const rp = require('request-promise')
const fs = require("fs")
const path = require("path")
const htmlToText = require('html-to-text')
const cheerio = require('cheerio')
const stripCommon = require('strip-common-words')

const page = 1
const perPage = 100 // max = 100

const tagDir = `${__dirname}/_tagged/`
const untagDir = `${__dirname}/_untagged/`

const url = `https://hn.algolia.com/api/v1/search_by_date?tags=show_hn&page=${page}&hitsPerPage=${perPage}`

// Fetch hn
rp({
    url: url,
    json: true
}).then(body => {

    body.hits.forEach(hit => {

        // Invalid entry or entry pointed to hn itself
        if (!hit.url || hit.url.indexOf("news.ycombinator.com") > 0) return

        const fileName = hit.url.replace(/(^\w+:|^)\/\//, '').replace(/\//g, "_") + ".json"

        // Already fetched
        if (fs.existsSync(`${tagDir}${fileName}`) || fs.existsSync(`${untagDir}${fileName}`)) return

        // Fetch the content
        rp({
            url: hit.url
        }).then(content => {

            let result = {
                _id: hit.objectID,
                site: hit.url,
                title: hit.title.replace("Show HN:", ""),
                author: hit.author,
                date: new Date(),
                tags: [],
                content: ""
            }

            // GitHub
            if (hit.url.indexOf("github.com/") > 0 && content.indexOf("#readme")) {

                const git = parseGithub(content)
                result.tags = git.tags
                result.content = git.text

                // Default
            } else {

                result.content = clean(htmlToText.fromString(content, { wordwrap: false, ignoreHref: true, ignoreImage: true, }), true)

            }

            // Write the result to file
            const savePath = (result.tags.length) ? `${tagDir}${fileName}` : `${untagDir}${fileName}`
            // const savePath = `${tagDir}${fileName}`

            fs.writeFile(savePath, JSON.stringify(result, null, '\t'), error => {
                if (error) {
                    console.log(`❌  ${hit.url}`, error)
                } else {
                    console.log(`🌎  ${hit.url}`)
                }
            })

        })

    })

}).catch(error => {
    console.log(error)
})

// * GITHUB * //
function parseGithub(body) {

    const $ = cheerio.load(body)

    let tags = {
        categories: [],
        languages: []   
    }

    $('.topic-tag-link').each(function (i, el) {
        tags.categories.push(clean($(this).text()))
    })

    $('.repository-lang-stats-graph .language-color').each(function (i, el) {
        tags.languages.push(clean($(this).text()))
    })

    // let text = clean($("#readme").find().not('pre').text(), true).replace('readme.md','')

    return {
        tags: tags,
        text: ''
    }

}

function clean(str, strip) {

    // Remove common english words
    if (strip) str = stripCommon(str)

    return str
        // remove non-ascii chars
        .replace(/[^\x00-\xFF]/g, "")
        // remove line breaks
        .replace(/(?:\r\n|\r|\n)/g, "")
        // remove literal line breaks
        .replace(/(?:\\[rn])+/g, "")
        // remove TABS
        .replace(/\t/g, "")
        // remove double spaces
        .replace(/ +(?= )/g, '')
        // lowercase?
        .toLowerCase()
        // trim
        .trim()

}
