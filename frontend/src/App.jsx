
import {useEffect,useState} from 'react'
import axios from 'axios'
export default function App(){
  const [notes,setNotes]=useState([])
  useEffect(()=>{axios.get('http://127.0.0.1:8000/api/notes/').then(r=>setNotes(r.data))},[])
  return (<div>
    <h1>DRF + React Connected</h1>
    {notes.map(n=><p key={n.id}>{n.title}</p>)}
  </div>)
}
