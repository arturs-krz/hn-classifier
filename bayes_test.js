const natural = new require('natural')
const classifier = new natural.BayesClassifier()
const fs = require("fs")

const tagDir = `${__dirname}/_tagged/`
const untagDir = `${__dirname}/_untagged/`



const aliasesPath = `${__dirname}/aliases.json`
fs.readFile(aliasesPath, (err, data) => {
    const aliases = JSON.parse(data)
    
    fs.readdir(tagDir, (err, files) => {
        let tagged = []

        let tagging = new Promise((resolve, reject) => {
            
            const totalFiles = files.length
            files.forEach((file, index) => { 
                if(file.indexOf('.json') !== -1) {
                    fs.readFile(`${tagDir}${file}`, (err, data) => {
                        let resource = JSON.parse(data)
                        console.log(file)
                        resource.popularTags = []
                        resource.tags.categories.forEach(category => {
                            aliases.forEach(alias => {
                                if(category == alias.tag || alias.aliases.indexOf(category) !== -1) {
                                    resource.popularTags.push(alias.tag)
                                }
                            })
                        })

                        resource.popularTags = resource.popularTags.filter((value, index, self) => self.indexOf(value) == index)
                        if(resource.popularTags.length) {
                            tagged.push(resource)
                            fs.writeFile(`${__dirname}/_popular/${file}`, JSON.stringify({
                                "title": resource.title,
                                "tags": resource.popularTags
                            }))
                        }

                        if(index == totalFiles - 1) resolve('success')
                    })
                }
            })

        })
        tagging.then(success => {
            console.log(`Tagged ${tagged.length}`)
            tagged.forEach(resource => {

                resource.popularTags.forEach(tag => {
                    // console.log(resource.title, tag)
                    classifier.addDocument(resource.title, tag)
                })
            })
            classifier.train()

            fs.readdir(untagDir, (err, files) => {
                files.forEach(file => {
                    fs.readFile(`${untagDir}${file}`, (err, data) => {
                        let resource = JSON.parse(data)

                        console.log(resource.title)
                        console.log(classifier.classify(resource.title))
                    })
                })
            })
        })
    })

    


})