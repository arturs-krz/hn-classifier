const natural = new require('natural')
// const classifier = new natural.BayesClassifier()
const fs = require("fs")
// const stripCommon = require('strip-common-words')

const tagDir = `${__dirname}/_customtags/`
const untagDir = `${__dirname}/_untagged/`

const bigClasses = ['development', 'tools']
let included = {}

const aliasesPath = `${__dirname}/custom_aliases.json`
fs.readFile(aliasesPath, (err, data) => {
    const aliases = JSON.parse(data)
    
    fs.readdir(tagDir, (err, files) => {
        let tagged = []
        let unknown = {}

        let tagging = new Promise((resolve, reject) => {
            
            const totalFiles = files.length
            files.forEach((file, index) => {

                if(file.indexOf('.json') !== -1) {
                    fs.readFile(`${tagDir}${file}`, (err, data) => {
                        let resource = JSON.parse(data)
                        console.log(file)

                        if(resource.tags.hasOwnProperty('categories')) {
                            resource.popularTags = []
                            resource.tags.categories.forEach(category => {
                                aliases.forEach(alias => {
                                    if(category != 'opensource' && (category == alias.tag || alias.aliases.indexOf(category) !== -1)) {
                                        resource.popularTags.push(alias.tag)
                                    } else {
                                        if(!unknown.hasOwnProperty(category)) unknown[category] = 0
                                        unknown[category] += 1
                                    }
                                })
                            })

                            // if(!resource.popularTags.length) {
                            //     resource.tags.languages.forEach(lang => {
                            //         aliases.forEach(alias => {
                            //             if(lang == alias.tag || alias.aliases.indexOf(lang) !== -1) {
                            //                 resource.popularTags.push(alias.tag)
                            //             }
                            //         })
                            //     })
                            // }

                            
                            if(resource.popularTags.length) {
                                resource.popularTags = resource.popularTags.filter((value, index, self) => self.indexOf(value) == index)
                                // let containsBig = resource.popularTags.reduce((acc, value) => {
                                //     if(bigClasses.indexOf(value) !== -1) return acc + 1
                                //     else return acc
                                // }, 0)
                                // if(resource.popularTags.length > containsBig) {
                                //     console.log('------')
                                //     console.log(containsBig)
                                //     console.log(resource.popularTags)
                                //     resource.popularTags = resource.popularTags.filter(value => bigClasses.indexOf(value) === -1)
                                //     console.log(resource.popularTags)
                                // }
                                // if (fs.existsSync(`${__dirname}/_popular/${file}`)) return
                                
                                tagged.push(resource)
                                fs.writeFile(`${__dirname}/_popular/${file}`, JSON.stringify({
                                    "title": clean(resource.title, false),
                                    "tags": resource.popularTags.map(tag => clean(tag))
                                }))
                            }
                        }

                        if(index == totalFiles - 1) resolve('success')
                    })
                }
            })

        })
        tagging.then(success => {
            console.log(`Tagged ${tagged.length}`)
            // tagged.forEach(resource => {

            //     resource.popularTags.forEach(tag => {
            //         // console.log(resource.title, tag)
            //         classifier.addDocument(resource.title, tag)
            //     })
            // })
            // classifier.train()

            // fs.readdir(untagDir, (err, files) => {
            //     files.forEach(file => {
            //         fs.readFile(`${untagDir}${file}`, (err, data) => {
            //             let resource = JSON.parse(data)

            //             console.log(resource.title)
            //             console.log(classifier.classify(resource.title))
            //         })
            //     })
            // })
        })
    })

    


})

function clean(str, strip) {

    // Remove common english words
    // if (strip) str = stripCommon(str)

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