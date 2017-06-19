const fs = require('fs')
const rp = require('request-promise')
const csv = require('csv-parse')
const cheerio = require('cheerio')
const stripCommon = require('strip-common-words')

const tagDir = `${__dirname}/_tagged/`
let csv_res = []
let total = 0

fs.readFile('./show_hn.csv', (err, data) => {
    csv(data, { delimiter: ';' }, (err, output) => {
        csv_res = output.filter(resource => resource[5].indexOf('github.com/') !== -1)
        total = csv_res.length
        fetch(3000)
    })
})

function fetch(idx) {
    let resource = csv_res[idx]
    let url = resource[5]

    let fileName = url.replace(/(^\w+:|^)\/\//, '').replace(/\//g, "_") + ".json"
    if (!fs.existsSync(`${tagDir}${fileName}`)) {
        rp({
            url: url
        }).then(content => {
            let result = {
                _id: resource[0],
                site: url,
                title: resource[4].replace("Show HN:", ""),
                author: resource[1],
                date: new Date(),
                tags: parseGithub(content).tags,
                content: ""
            }
            console.log(result)


            fs.writeFile(`${tagDir}${fileName}`, JSON.stringify(result, null, '\t'), error => {
                if (error) {
                    console.log(`❌  ${url}`, error)
                } else {
                    console.log(`🌎  ${url}`)
                }
            })



            if (idx < total - 1) fetch(idx + 1)
        })
            .catch(error => {
                if (idx < total - 1) fetch(idx + 1)
            })
    }
}

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