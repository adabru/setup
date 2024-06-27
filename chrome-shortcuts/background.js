chrome.commands.onCommand.addListener(function(command) {
  console.log('Command:', command);
  switch(command){
    case 'next_tab':
      chrome.tabs.query({currentWindow:true}, (tabs) => {
        nextTab = tabs[(tabs.findIndex((t) => t.active) + 1) % tabs.length].id
        chrome.tabs.update(nextTab, {active: true})
      })
      break
    case 'previous_tab':
      chrome.tabs.query({currentWindow:true}, (tabs) => {
        previousTab = tabs[(tabs.findIndex((t) => t.active) + tabs.length - 1) % tabs.length].id
        chrome.tabs.update(previousTab, {active: true})
      })
      break
    case 'close_tab':
      chrome.tabs.query({active:true, currentWindow:true}, (tabs) => {
        chrome.tabs.remove(tabs[0].id)
      })
      break
    case 'create_tab':
      chrome.tabs.create({})
    case 'history_backward':
      // does not work on chrome:// urls (see https://developer.chrome.com/extensions/match_patterns)
      // could be solved with https://stackoverflow.com/a/24606853/6040478
      chrome.tabs.executeScript({code: "window.history.go(-1)", runAt: "document_start"})
      break
    case 'history_forward':
      chrome.tabs.executeScript({code: "window.history.go(1)", runAt: "document_start"})
      break
  }
})
