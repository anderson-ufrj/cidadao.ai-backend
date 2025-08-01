import React from 'react';
import {Redirect} from '@docusaurus/router';

export default function Home(): JSX.Element {
  // Redireciona automaticamente para /docs/intro
  return <Redirect to="docs/intro" />;
}