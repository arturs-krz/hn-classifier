const fs = require("fs")

const githubDir = `${__dirname}/_tagged/`
const taggedDir = `${__dirname}/_customtags/`
const pickDir = `${__dirname}/_customtags/_picked/`

const keywords = [
    'game', 'blockchain', 'music', 'spotify', 'audio',
    'media', 'learning', 'neural', 'machine', 'bot',
    'chat', 'processing', 'phaser', 'webgl', 'opengl', 'directx',
    'design', 'css', 'ios', 'mac', 'apple', 'macos', 'cloud',
    'gaming', 'hack', 'tensorflow', 'theano', 'docker',
    'cubernetes', 'sass', 'cordova', 'animat', 'visualizat', 
    'graphics', 'responsive', 'image', 'art', 'video', 
    'slack', 'reddit', 'youtube', 'soundcloud', 'jpeg',
    'crypto', 'bitcoin', 'ethereum', 'watchos', 'analysis', 
    'dataset', 'science', 'framework', 'library'
]

fs.readdir(taggedDir, (err, tagged) => {
    fs.readdir(githubDir, (err, files) => {
        files = files.filter(file => tagged.indexOf(file) === -1)  
        
        files.forEach((file, index) => {
            if(file.indexOf('.json') !== -1) {
                fs.readFile(`${githubDir}${file}`, (err, data) => {
                    let resource = JSON.parse(data)
                    keywords.forEach(keyword => {
                        if(resource.title.indexOf(keyword) !== -1) {
                            fs.writeFile(`${pickDir}${file}`, data)
                            return
                        }
                    })
                })
            }
        })
    })
})