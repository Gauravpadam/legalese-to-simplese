import React, { useState } from 'react'

import AnalysisContext from './AnalysisContext'

const AnalysisContextProvider = ({children}) => {

    const [analysis,setAnalysis] = useState(null)

  return (
    <AnalysisContext.Provider value={{analysis,setAnalysis}}>
        {children}
    </AnalysisContext.Provider>
  )
}

export default AnalysisContextProvider