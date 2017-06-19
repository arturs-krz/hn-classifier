const fs = require("fs")
const tagDir = `${__dirname}/_tagged/`

const categories = {}
const languages = {}


fs.readdir(tagDir, (err, files) => {
    let totalFiles = files.length
    let counted = new Promise((resolve, reject) => {
        files.forEach((file, index) => {
            if (file.indexOf('.json') !== -1) {
                fs.readFile(`${tagDir}${file}`, (err, data) => {
                    let resource = JSON.parse(data)
                    // console.log(resource.tags)
                    if (resource.tags.hasOwnProperty('categories')) {
                        const cats = resource.tags.categories
                        const langs = resource.tags.languages

                        cats.forEach(cat => {
                            if(!categories.hasOwnProperty(cat)) categories[cat] = 0 
                            categories[cat] += 1
                        })
                        langs.forEach(lang => {
                            if(!languages.hasOwnProperty(lang)) languages[lang] = 0
                            languages[lang] += 1
                        })
                    }
                    if (index == totalFiles - 1) resolve('done')
                })
            }
        })
    })

    counted.then(done => {
        let sortedCats = []
        for(cat in categories) {
            sortedCats.push({tag: cat, count: categories[cat]})
        }
        sortedCats.sort((a,b) => b.count - a.count)
        fs.writeFile(`${__dirname}/popular_categories.json`, JSON.stringify(sortedCats, null, 4))

        let sortedLangs = []
        for(lang in languages) {
            sortedLangs.push({tag: lang, count: languages[lang]})
        }
        sortedLangs.sort((a,b) => b.count - a.count)
        fs.writeFile(`${__dirname}/popular_languages.json`, JSON.stringify(sortedLangs, null, 4))
    })
})

