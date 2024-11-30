import { lazy } from 'react'
import { Route, Routes } from 'react-router-dom'
import { DefaultLayout, Flex, Text } from 'shared/ui'
import { BoardMenu } from 'widgets/BoardMenu/ui'

const HomePage = lazy(() => import('./home'))
const UploadPage = lazy(() => import('./upload'))
const FilesPage = lazy(() => import('./files'))
const FilePage = lazy(() => import('./file'))

export default function Routing() {
  return (
    <DefaultLayout>
      <Flex h="100%" w="85px">
        <BoardMenu />
      </Flex>
      <Routes>
        <Route path={'/'} element={<UploadPage />} />
        <Route path={'/home'} element={<HomePage />} />
        <Route path={'/files'} element={<FilesPage />} />
        <Route path={'/file/:id'} element={<FilePage />} />
        <Route
          path={'*'}
          element={
            <Flex w="100%" h="100%" justifyContent="center" alignItems="center">
              <Text>404 page</Text>
            </Flex>
          }
        />
      </Routes>
    </DefaultLayout>
  )
}
