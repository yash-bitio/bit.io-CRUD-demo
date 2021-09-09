import React, { useState, useEffect, useRef } from 'react';
import { Container, Header, Button, Input, Card, Feed, Icon, Loader } from 'semantic-ui-react'
import 'semantic-ui-css/semantic.min.css'

import './App.css';

import { eel } from "./eel.js";

// Point Eel web socket to the instance
eel.set_host("ws://localhost:8888");

export default function App() {
  const [newListName, setNewListName] = useState("")
  const [newItem, setNewItem] = useState("")
  const [lists, setLists] = useState([])
  const [loading, setLoading] = useState(false)
  
  useEffect(() => {
    eel.create_repo()
    refreshLists()
  }, []);

  const refreshLists = () => {
    setLoading(true);
    eel.getLists()(data => {
      setLists(data)
      setLoading(false);
    });
  }

  const createNewList = () => {
    eel.createNewList(newListName)(() => {
      setNewListName("")
      refreshLists()
    });
  }

  const createNewItem = (key) => {
    eel.createNewItem(newItem, key)(() => {
      setNewItem("")
      refreshLists()
    });
  }

  const updateTask = (id, status) => {
    eel.updateItem(id, status)(() => {
      refreshLists()
    });
  }

  const delete_list = (key) => {
    eel.archiveList(key)(() => {
      refreshLists()
    });
  }

  const delete_item = (id) => {
    eel.delete_item(id)(() => {
      refreshLists()
    });
  }

  return (
    <Container style={{display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', paddingTop: '40px'}}>
      <div>
        <Header as='h1'>To-Do View</Header>
        <Loader active={loading} inline='centered' />
      </div>
      <br/>
      <div style={{ display: 'flex', flexDirection: 'row' }}>
        <Input value={newListName} onChange={(e) => setNewListName(e.target.value)} placeholder='List Name' style={{marginRight: '10px'}} />
        <Button onClick={createNewList}>Create New List</Button>
      </div>
      <div style={{paddingTop: '20px'}}>
        {lists.map((data, index) => (
          <Card>
            <Card.Content>
              <Card.Header>{data.list_name}<Icon onClick={() => delete_list(data.key)} size='small' name='close' style={{color: '#EF4444', marginLeft: '5px'}} /></Card.Header>
              <div style={{ display: 'flex', flexDirection: 'row', height: '30px', marginTop: '4px' }}>
                <Input onChange={(e) => setNewItem(e.target.value)} placeholder='Get milk...' style={{marginRight: '10px'}} />
                <Button onClick={() => createNewItem(data.key)}><Icon size='small' name='add' style={{display: 'flex', justifyContent: 'center', alignItems: 'center'}} /></Button>
              </div>
            </Card.Content>
            <Card.Content>
              <Feed>
                {data.list_items.map((list_item_data, index) => (
                  <Feed.Event>
                    <Feed.Content>
                      <Feed.Summary onClick={() => updateTask(list_item_data.id, !list_item_data.completed)} style={{ backgroundColor: list_item_data.completed == true ? '#6EE7B7' : '#FDE68A', borderRadius: '5px', padding: '2px', paddingLeft: '10px', color: '#111827' }}>
                        {list_item_data.message}<Icon onClick={() => delete_item(list_item_data.id)} size='small' name='close' style={{color: '#EF4444', marginLeft: '5px'}} />
                      </Feed.Summary>
                    </Feed.Content>
                  </Feed.Event>  
                ))}
              </Feed>
            </Card.Content>
          </Card>
        ))}
      </div>
    </Container>
  );
}
